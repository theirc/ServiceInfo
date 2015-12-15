var gulp = require('gulp')
,   rename = require('gulp-rename')
,   less = require('gulp-less')
,   bg = require('gulp-bg')
,   gutil = require('gulp-util')
,   browserify = require('gulp-browserify')
,   minimist = require('minimist')
,   sync_exec = require('sync-exec')
,   rtlcss = require('gulp-rtlcss')
,   rename = require('gulp-rename')
;

var knownOptions = {
    default: {
        config: "base"
        , fast: false
        , port: 8000
        , app: true
        , cms: true
    }
};

var options = minimist(process.argv.slice(2), knownOptions);

var API_PORT = 4005;
var EXPRESS_PORT = options.port;
var EXPRESS_ROOT = __dirname + "/frontend";
var LIVERELOAD_PORT = 3572;

gulp.task('noop', function () {});

gulp.task('startExpress', ['build'], function() {
    var express = require('express');
    var app = express();
    app.use('/media', express.static(__dirname + "/public/media"));
    app.use(require('connect-livereload')());
    app.use(express.static(EXPRESS_ROOT));
    app.listen(EXPRESS_PORT);
});

gulp.task('startDjango', function() {
    bg("python", "manage.py", "runserver", API_PORT)();
});

gulp.task('startLiveReload', ['startExpress'], function() {
    lr = require('tiny-lr')();
    lr.listen(LIVERELOAD_PORT);
});

gulp.task('injectEnvConfig', function(cb) {
    gulp.src("frontend/config." + options.config + ".json")
        .pipe(rename("config.json"))
        .pipe(gulp.dest("frontend"))
        .on('end', function(){cb();})
    ;
});

function compile_less (src, dest, cb) {
    gulp.src(src)
        .pipe(less())
        .pipe(gulp.dest(dest))
        .on('end', function () { cb(); })
        ;
}

gulp.task('compile_less_app', function (cb) {
  compile_less(
      'frontend/styles/site-*.less'
      , 'frontend/styles'
      , cb
  );
});

gulp.task('compile_less_cms', function (cb) {
  compile_less(
      'service_info/static/less/site.less'
      , 'service_info/static/css'
      , cb
  );

  gulp.src('service_info/static/less/site.less')
    .pipe(less())
    .pipe(rtlcss())
    .pipe(rename({ suffix: '-rtl' }))
    .pipe(gulp.dest('service_info/static/css'))
  ;

  gulp.src('node_modules/materialize-css/dist/css/materialize.min.css')
    .pipe(gulp.dest('service_info/static/css'))
    .pipe(rtlcss())
    .pipe(rename({ suffix: '-rtl' }))
    .pipe(gulp.dest('service_info/static/css'))
  ;
});

gulp.task('compile_less', [
  options.app ? 'compile_less_app' : 'noop'
  , options.cms ? 'compile_less_cms' : 'noop'
], function () {});

function browserify_wrap (src, dest, cb) {
    /* When the templates compile themselves, have them use our
       own 'compiler' module so we can register some helpers on it
       first:
     */
    var hbsfy = require('hbsfy').configure({
        compiler: "require('../compiler')",
        extensions: ['hbs'],
        precompilerOptions: {
            knownHelpersOnly: true,
            knownHelpers: {
                multiline: true,
                toLowerCase: true
            },
            strict: true
        }
    });

    gulp.src(src)
        .pipe(browserify({
            insertGlobals : true,
            debug : options.config !== 'production',
            transform: [hbsfy]
        }))
        .pipe(rename('bundle.js'))
        .pipe(gulp.dest(dest))
        .on('end', function(){cb();})
        ;
}

gulp.task('browserify_app', function (cb) {
  browserify_wrap(
      'frontend/index.js'
      , 'frontend'
      , cb
  );
});

gulp.task('browserify_cms', function browserify_cms (cb) {
  browserify_wrap(
      'service_info/static/js/src/index.js'
      , 'service_info/static/js/dist'
      , cb
  );
});

gulp.task('browserify', [
  options.app ? 'browserify_app' : 'noop'
  , options.cms ? 'browserify_cms' : 'noop'
], function () {});

function closure (src, dest, out, cb) {
    if (options.fast) {
        sync_exec(['cp', src, dest + '/' + out].join(' '));
    } else {
        var res = sync_exec(
            ['ccjs', src, '--language_in=ECMASCRIPT5'].join(' ')
        );
        if (res.stderr) {
            console.error(res.stderr);
        }
        if (res.stdout) {
            var string_src = function(filename, string) {
              var src = require('stream').Readable({ objectMode: true });
              src._read = function () {
                this.push(new gutil.File({ cwd: "", base: "", path: filename, contents: new Buffer(string) }));
                this.push(null);
              };
              return src;
            };
            string_src(out, res.stdout)
                .pipe(gulp.dest(dest))
            ;
        } else {
            throw new gutil.PluginError({
              plugin: "Closure",
              message: 'Failed to compile JS.'
            });
        }
    }
    cb();
}

gulp.task('closure_app', ['browserify_app'], function (cb) {
  closure(
      'frontend/bundle.js'
      , 'frontend'
      , 'bundle_min.js'
      , cb
  );
});

gulp.task('closure_cms', ['browserify_cms'], function (cb) {
  closure(
      'service_info/static/js/dist/bundle.js'
      , 'service_info/static/js/dist'
      , 'bundle.min.js'
      , cb
  );
});

gulp.task('closure', [
  options.app ? 'closure_app' : 'noop'
  , options.cms ? 'closure_cms' : 'noop'
], function() {});

gulp.task('build', ['closure', 'compile_less', 'injectEnvConfig'], function(){});

// Notifies livereload of changes detected
// by `gulp.watch()`
// FIXME: This is still a function because I can't figure out how
// to get the event object if I change this to a task.
function notifyLivereload(event) {

    // `gulp.watch()` events provide an absolute path
    // so we need to make it relative to the server root
    var fileName = require('path').relative(EXPRESS_ROOT, event.path);
    if (fileName.match(/bundle/)) {
        return;
    }

    gulp.run('build');

    setTimeout(function(){
        lr.changed({
            body: {
                files: [fileName]
            }
        });
    }, 500); // For some reason, triggering live reload too early serves the old version
}

gulp.task('default', ['startLiveReload', 'startDjango'], function() {
    gulp.watch(
        [
            'frontend/index.html'
            , 'frontend/**/*.js'
            , 'frontend/styles/site.less'
            , 'frontend/templates/*.hbs'
            , 'frontend/views/*.js'
            , 'service_info/static/less/*.less'
            , 'service_info/static/less/**/*.less'
            , 'service_info/static/js/src/*.js'
            , 'service_info/static/js/src/**/*.js'
        ]
        , notifyLivereload
    );
});

var gulp = require('gulp')
,   rename = require('gulp-rename')
,   less = require('gulp-less')
,   bg = require('gulp-bg')
,   gutil = require('gulp-util')
,   browserify = require('gulp-browserify')
,   minimist = require('minimist')
,   sync_exec = require('sync-exec')
;

var knownOptions = {
    default: {
        config: "base",
        fast: false,
        port: 8000
    }
}

var options = minimist(process.argv.slice(2), knownOptions);

var API_PORT = 4005;
var EXPRESS_PORT = options.port;
var EXPRESS_ROOT = __dirname + "/frontend";
var LIVERELOAD_PORT = 3572;

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
}
);

gulp.task('compile_less', function (cb) {
    gulp.src('frontend/styles/site-*.less')
        .pipe(less())
        .pipe(gulp.dest('frontend/styles'))
        .on('end', function(){cb();})
    ;
});

gulp.task('browserify', function(cb) {
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

    gulp.src('frontend/index.js')
        .pipe(browserify({
            insertGlobals : true,
            debug : options.config !== 'production',
            transform: [hbsfy]
        }))
        .pipe(rename('bundle.js'))
        .pipe(gulp.dest('frontend'))
        .on('end', function(){cb();})
});

gulp.task('closure', ['browserify'], function(cb) {
    if (options.fast) {
        sync_exec('cp frontend/bundle.js frontend/bundle_min.js');
    } else {
        var res = sync_exec(
            'ccjs frontend/bundle.js --language_in=ECMASCRIPT5'
        );
        if (res.stderr) {
            console.error(res.stderr);
        }
        if (res.stdout) {
            function string_src(filename, string) {
              var src = require('stream').Readable({ objectMode: true })
              src._read = function () {
                this.push(new gutil.File({ cwd: "", base: "", path: filename, contents: new Buffer(string) }))
                this.push(null)
              }
              return src
            }
            string_src("bundle_min.js", res.stdout)
                .pipe(gulp.dest('frontend'))
            ;
        } else {
            throw new gutil.PluginError({
              plugin: "Closure",
              message: 'Failed to compile JS.'
            });
        }
    }
    cb();
});

gulp.task('build', ['closure', 'compile_less', 'injectEnvConfig'], function(){});

// Notifies livereload of changes detected
// by `gulp.watch()`
// FIXME: This is still a function because I can't figure out how
// to get the event object if I change this to a task.
function notifyLivereload(event) {

    // `gulp.watch()` events provide an absolute path
    // so we need to make it relative to the server root
    var fileName = require('path').relative(EXPRESS_ROOT, event.path);

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
    gulp.watch(['frontend/index.html', 'frontend/index.js', 'frontend/router.js',
                'frontend/styles/site.less', 'frontend/templates/*.hbs', 'frontend/views/*.js'],
                notifyLivereload);
});


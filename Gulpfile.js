var gulp = require('gulp')
,   rename = require('gulp-rename')
,   less = require('gulp-less')
,   browserify = require('gulp-browserify')
;

var EXPRESS_PORT = 8000;
var EXPRESS_ROOT = __dirname + "/frontend";
var LIVERELOAD_PORT = 35729;

function startExpress() {
    build();

    var express = require('express');
    var app = express();
    app.use(require('connect-livereload')());
    app.use(express.static(EXPRESS_ROOT));
    app.listen(EXPRESS_PORT);
}

function startLiveReload() {
    lr = require('tiny-lr')();
    lr.listen(LIVERELOAD_PORT);
}

function build() {
    gulp.src('frontend/styles/*.less')
        .pipe(less())
        .pipe(gulp.dest('frontend/styles'))
    ;

    gulp.src('frontend/index.js')
        .pipe(browserify({
            insertGlobals : true,
            debug : !gulp.env.production,
            transform: ['hbsfy'],
        }))
        .pipe(rename('bundle.js'))
        .pipe(gulp.dest('frontend'))
    ;
}

// Notifies livereload of changes detected
// by `gulp.watch()`
function notifyLivereload(event) {

    // `gulp.watch()` events provide an absolute path
    // so we need to make it relative to the server root
    var fileName = require('path').relative(EXPRESS_ROOT, event.path);

    build();

    lr.changed({
        body: {
            files: [fileName]
        }
    });
}

gulp.task('default', function() {
    startExpress();
    startLiveReload();
    gulp.watch(['frontend/index.html', 'frontend/index.js', 'frontend/router.js', 'frontend/styles/site.less', 'frontend/templates/*.html', 'frontend/views/*.js'], notifyLivereload);
});

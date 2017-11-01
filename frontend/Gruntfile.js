module.exports = function(grunt) {
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        concat: {
            options: {
                separator: ';'
            },
            dist: {
                src: ['src/js/app.js'],
                dest: 'dist/js/app.js'
            }
        },
        copy: {
            main: {
                expand: true,
                cwd: 'static',
                src: '**',
                dest: 'dist/',
            }
        },
        uglify: {
            options: {
                banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
            },
            dist: {
                files: {
                    'static/js/app.min.js': ['<%= concat.dist.dest %>']
                }
            }
        }
    });
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.registerTask('default', ['concat', 'uglify', 'copy']);
};

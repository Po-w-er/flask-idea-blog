from flask import Blueprint, render_template

error = Blueprint("error",__name__, template_folder='template')


@error.app_errorhandler(404)
def error_404(error):
    return render_template("error_404.html"), 404


@error.app_errorhandler(403)
def error_403(error):
    return render_template("error_403.html"), 403


@error.app_errorhandler(500)
def error_500(error):
    return render_template("error_500.html"), 500



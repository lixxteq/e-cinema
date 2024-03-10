from flask import Blueprint, abort, render_template, request, current_app
import requests

controller = Blueprint('watch', __name__, url_prefix='/watch')

@controller.route('<string:composite_id>')
def watch(composite_id):
    media_source = requests.get(
        url = f'{current_app.config["SERVICE_URI"]}/source/{composite_id}'
    )
    if media_source.ok:
        return render_template('player.html', media_source=media_source)
    abort(404)
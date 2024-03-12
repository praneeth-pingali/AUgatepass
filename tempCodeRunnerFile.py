app.route('/wrong')
def wrong():
    session["login_type"] = 'wrongggg'
    return render_template('wrong.html')
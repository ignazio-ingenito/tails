# -*- coding: utf-8 -*-

from webapp import app

if __name__ == "__main__":
    app.run(port=8080, debug=True, threaded=True)

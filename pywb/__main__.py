"""
Main entry used with 'python -m'
"""

try:
    from pywb import app

    if __name__ == "__main__":
        app.run()
except KeyboardInterrupt:
    pass

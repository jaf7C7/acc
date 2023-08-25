from acc.main import Application


def main(argv) -> int:
    """Handles creating and running an Application instance"""
    app = Application()
    return app.run(argv)

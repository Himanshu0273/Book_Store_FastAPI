from app.config.load_config import api_settings
from app.f_api import f_api


@f_api.get("/", tags=["Root"])
def read_root():
    return {
        "message": "running",
        "payload": "Welcome to E-Insurance API",
        "status_code": 200,
    }


def run_web_mode():
    try:
        import uvicorn

        host_ip_address = api_settings.HOST_IP_ADDRESS
        host_port_number = api_settings.HOST_PORT_NUMBER

        uvicorn.run(
            "app.f_api:f_api", host=host_ip_address, port=host_port_number, reload=True
        )

    except Exception as e:
        print(f"Error Occured: {e}")


if __name__ == "__main__":
    run_web_mode()

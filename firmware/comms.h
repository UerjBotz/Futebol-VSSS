#ifdef ESP32
    #include <WiFi.h>
    #include <esp_now.h>
#else
    #include <ESP8266WiFi.h>
    #include <esp_now.h>
#endif

#define BAUD_RATE 115200

typedef struct packet {
    uint8_t id;
    uint8_t len;
    char vels[25];
} Packet;

void init_wifi(wifi_mode_t mode=WIFI_STA) {
    WiFi.mode(mode);
    WiFi.STA.begin();

    esp_err_t err = esp_now_init();
    assert (err == ESP_OK);
}

uint8_t* get_mac_addr() {
    static uint8_t mac_addr[6];
    return WiFi.macAddress(mac_addr);
}


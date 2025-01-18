#include <Arduino.h>

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

uint8_t* get_mac_addr(wifi_interface_t interface=WIFI_IF_STA) {
    static uint8_t mac_addr[6];
    return WiFi.macAddress(mac_addr);
}

Packet msg;
void on_recv(const uint8_t* mac, const uint8_t* data, int len) {
    memcpy(&msg, data, sizeof(msg));

    Serial.print("Bytes received: "); Serial.println(len);
    Serial.print("kind: "); Serial.println(msg.id);
    Serial.print("len: ");  Serial.println(msg.len);
    Serial.print("vels: "); Serial.println(msg.vels);

    Serial.println();
}

void setup() {
    init_wifi();
    uint8_t* mac_addr = get_mac_addr();

    Serial.begin(BAUD_RATE);
    Serial.printf("%02x:%02x:%02x:%02x:%02x:%02x\n",
                  mac_addr[0], mac_addr[1], mac_addr[2],
                  mac_addr[3], mac_addr[4], mac_addr[5]);

    esp_now_register_recv_cb(esp_now_recv_cb_t(on_recv));
}

void loop() {}

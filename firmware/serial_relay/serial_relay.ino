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

uint8_t peer_addr[6] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};

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

//! ver se realmente precisa pra checar o status
void on_send(const uint8_t *mac_addr, esp_now_send_status_t status) {
    Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
}

char input[255] = {0};
void setup() {
    init_wifi();
    uint8_t* mac_addr = get_mac_addr();

    Serial.begin(BAUD_RATE);
    Serial.printf("%02x:%02x:%02x:%02x:%02x:%02x\n",
                  mac_addr[0], mac_addr[1], mac_addr[2],
                  mac_addr[3], mac_addr[4], mac_addr[5]);

    static esp_now_peer_info_t peer {
        .channel = 0,
        .encrypt = false,
    };
    memcpy(peer.peer_addr, peer_addr, sizeof(peer_addr));
    
    esp_err_t err = esp_now_add_peer(&peer);
    assert (err == ESP_OK);

    esp_now_register_send_cb(on_send);
}

void loop() {
    const char sentinel = '\n';

    for (auto buf = input; Serial.available(); buf++) {
        *buf = (char) Serial.read();
        if (*buf == sentinel) {
            *buf = '\0';
            Packet msg {
                .id = 0,
                .len  = strlen(input),
            };
            strcpy(msg.vels, input);
            Serial.println(input);

            esp_err_t err = esp_now_send(peer_addr, (uint8_t*) &msg, sizeof(msg));
            if (err == ESP_OK) Serial.println("Sent with success");
            else               Serial.println("Error sending the data");
        }
    }
    // esse loop lê da serial até encontrar um \n e aí faz broadcast via espnow
    // se a mensagem parar de chegar antes disso, ele ignora
    // detalhe: Serial.available() retorna quantos bytes tão disponíveis
}

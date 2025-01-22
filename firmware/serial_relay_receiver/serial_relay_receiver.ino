#include <Arduino.h>
#include "../comms.h"

#define ID 0 /*! mudar pra cada robô !*/
#define BAUD_RATE 115200

#define LEN(arr) (sizeof(arr)/sizeof(*arr))


struct vel { uint16_t esq=0, dir=0; };
union vels {
    uint16_t raw[6];
    struct vel at[3];
};

union vels convert_vel(char *const text, uint8_t len) {
    uint8_t v = 1, seps[6] = {0};
    for (int i = 0; (text[i] != '\0') && (i < len); i++) {
        if (text[i] == ' ') seps[v++] = i;
    }

    union vels vels{0};
    for (int i = 0; i < LEN(seps); i++) {
        vels.raw[i] = atoi(&text[seps[i]]);
    }
    return vels;
}

union vels vels{0};
void on_recv(const uint8_t* mac, const uint8_t* data, int len) {
    //! print
    Packet* msg = (Packet*) (void*)data;
    Serial.print("Bytes received: "); Serial.println(len);
    Serial.print("kind: "); Serial.println(msg->id);
    Serial.print("len:  "); Serial.println(msg->len);
    Serial.print("vels: "); Serial.println(msg->vels);
    Serial.println();

    //! print
    vels = convert_vel(msg->vels, msg->len);
    Serial.printf("robôs %d %d, %d %d, %d %d\n",
                vels.at[0].esq, vels.at[0].dir,
                vels.at[1].esq, vels.at[1].dir,
                vels.at[2].esq, vels.at[2].dir);
    Serial.println();
}

void setup() {
    init_wifi();
    uint8_t* mac_addr = get_mac_addr();

    Serial.begin(BAUD_RATE);
    Serial.printf("MAC: %02x:%02x:%02x:%02x:%02x:%02x\n",
                  mac_addr[0], mac_addr[1], mac_addr[2],
                  mac_addr[3], mac_addr[4], mac_addr[5]);
    Serial.printf("ID: %d", ID);

    esp_now_register_recv_cb(esp_now_recv_cb_t(on_recv));
}

void loop() {
    //! setar velocidades dos motores
}

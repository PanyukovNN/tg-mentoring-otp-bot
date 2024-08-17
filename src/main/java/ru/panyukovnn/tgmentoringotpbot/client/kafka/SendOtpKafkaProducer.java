package ru.panyukovnn.tgmentoringotpbot.client.kafka;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;
import ru.panyukovnn.tgmentoringotpbot.dto.SendMessageResponse;
import ru.panyukovnn.tgmentoringotpbot.util.JsonUtil;

@Slf4j
@Service
@RequiredArgsConstructor
@ConditionalOnProperty(prefix = "bot.kafka.send-otp", name = "enabled", havingValue = "true")
public class SendOtpKafkaProducer {

    @Value("${bot.kafka.send-otp.topic-out}")
    private String topic;

    private final JsonUtil jsonUtil;
    private final KafkaTemplate<String, String> kafkaTemplate;

    public void sendResponse(SendMessageResponse response) {
        try {
            String jsonResponse = jsonUtil.toJson(response);

            kafkaTemplate.send(topic, jsonResponse)
                .thenAccept(sendResult -> log.info("Ответ отправлен: {}", sendResult));
        } catch (Exception e) {
            log.error("Ошибка при отправке овтета в kafka: {}", e.getMessage(), e);
        }
    }
}

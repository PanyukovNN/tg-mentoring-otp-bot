package ru.panyukovnn.tgmentoringotpbot.listener;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.slf4j.MDC;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;
import ru.panyukovnn.tgmentoringotpbot.dto.SendMessageRequest;
import ru.panyukovnn.tgmentoringotpbot.service.SendTgMessageProcessor;
import ru.panyukovnn.tgmentoringotpbot.util.JsonUtil;

import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
@ConditionalOnProperty(prefix = "bot.kafka.send-otp", name = "enabled", havingValue = "true")
public class SendOtpKafkaListener {

    private final JsonUtil jsonUtil;
    private final SendTgMessageProcessor sendTgMessageProcessor;

    @KafkaListener(topics = "${bot.kafka.send-otp.topic-in}")
    public void consumeSendOtp(ConsumerRecord<String, String> consumerRecord) {
        MDC.put("requestId", UUID.randomUUID().toString());

        try {
            log.info("Получен запрос на отпрвку сообщения: {}", consumerRecord);

            String content = consumerRecord.value();
            SendMessageRequest sendRequest = jsonUtil.fromJson(content, SendMessageRequest.class);

            sendTgMessageProcessor.processSendTgMessage(sendRequest);
        } catch (Exception e) {
            log.error("Ошибка обработки сообщения топика : {}", e.getMessage(), e);
        } finally {
            MDC.clear();
        }
    }
}

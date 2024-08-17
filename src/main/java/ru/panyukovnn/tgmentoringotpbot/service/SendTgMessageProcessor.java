package ru.panyukovnn.tgmentoringotpbot.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.telegram.telegrambots.meta.api.methods.send.SendMessage;
import ru.panyukovnn.tgmentoringotpbot.client.kafka.SendOtpKafkaProducer;
import ru.panyukovnn.tgmentoringotpbot.config.TgBotApi;
import ru.panyukovnn.tgmentoringotpbot.dto.SendMessageRequest;
import ru.panyukovnn.tgmentoringotpbot.dto.SendMessageResponse;
import ru.panyukovnn.tgmentoringotpbot.dto.SendMessageStatus;

@Slf4j
@Service
@RequiredArgsConstructor
public class SendTgMessageProcessor {

    private final TgBotApi botApi;
    private final SendOtpKafkaProducer sendOtpKafkaProducer;

    public void processSendTgMessage(SendMessageRequest sendRequest) {
        try {
            botApi.execute(SendMessage.builder()
                .chatId(sendRequest.getTelegramChatId())
                .text(sendRequest.getMessage())
                .build());

            SendMessageResponse response = SendMessageResponse.builder()
                .id(sendRequest.getId())
                .status(SendMessageStatus.SUCCESS)
                .build();

            sendOtpKafkaProducer.sendResponse(response);
        } catch (Exception e) {
            log.warn("Не удалось отправить сообщение в чат. Запрос: {}. Ошибка: {}", sendRequest, e.getMessage(), e);

            SendMessageResponse response = SendMessageResponse.builder()
                .id(sendRequest.getId())
                .status(SendMessageStatus.ERROR)
                .errorMessage("Не удалось отправить сообщение в чат: " + e.getMessage())
                .build();

            sendOtpKafkaProducer.sendResponse(response);
        }
    }
}

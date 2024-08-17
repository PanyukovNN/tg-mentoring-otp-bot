package ru.panyukovnn.tgmentoringotpbot.dto;

import lombok.Data;

@Data
public class SendMessageRequest {

    private String id;
    private String telegramChatId;
    private String message;
}

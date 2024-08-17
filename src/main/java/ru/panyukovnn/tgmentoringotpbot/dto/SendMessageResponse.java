package ru.panyukovnn.tgmentoringotpbot.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class SendMessageResponse {

    private String id;
    private SendMessageStatus status;
    private String errorMessage;
}

package ru.panyukovnn.tgmentoringotpbot.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.Builder;
import lombok.Data;

@Data
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
public class SendMessageResponse {

    private String id;
    private SendMessageStatus status;
    private String errorMessage;
}

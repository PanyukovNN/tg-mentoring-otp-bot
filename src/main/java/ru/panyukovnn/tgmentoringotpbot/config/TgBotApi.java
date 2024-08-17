package ru.panyukovnn.tgmentoringotpbot.config;

import lombok.RequiredArgsConstructor;
import org.springframework.context.ApplicationEventPublisher;
import org.telegram.telegrambots.extensions.bots.commandbot.TelegramLongPollingCommandBot;
import org.telegram.telegrambots.meta.api.objects.Update;

@RequiredArgsConstructor
public class TgBotApi extends TelegramLongPollingCommandBot {

    private final ApplicationEventPublisher eventPublisher;
    private final String username;
    private final String token;

    @Override
    public String getBotUsername() {
        return this.username;
    }

    @Override
    public String getBotToken() {
        return this.token;
    }

    @Override
    public void processNonCommandUpdate(Update update) {
        eventPublisher.publishEvent(update);
    }
}

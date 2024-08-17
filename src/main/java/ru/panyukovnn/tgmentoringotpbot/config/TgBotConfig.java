package ru.panyukovnn.tgmentoringotpbot.config;

import org.springframework.context.ApplicationEventPublisher;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.telegram.telegrambots.extensions.bots.commandbot.commands.BotCommand;
import org.telegram.telegrambots.meta.TelegramBotsApi;
import org.telegram.telegrambots.meta.exceptions.TelegramApiException;
import org.telegram.telegrambots.updatesreceivers.DefaultBotSession;
import ru.panyukovnn.tgmentoringotpbot.property.TLBotProperties;

import java.util.List;

@Configuration
public class TgBotConfig {

    @Bean
    public TgBotApi botApi(ApplicationEventPublisher eventPublisher, TLBotProperties botProperties, List<BotCommand> commands) throws TelegramApiException {
        TgBotApi botApi = new TgBotApi(eventPublisher, botProperties.getName(), botProperties.getToken());

        new TelegramBotsApi(DefaultBotSession.class).registerBot(botApi);
        commands.forEach(botApi::register);

        System.out.println("registered");

        return botApi;
    }
}

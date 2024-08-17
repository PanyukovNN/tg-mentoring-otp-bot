package ru.panyukovnn.tgmentoringotpbot.listener;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Service;
import org.telegram.telegrambots.meta.api.objects.Update;

@Slf4j
@Service
@RequiredArgsConstructor
public class TgBotListener {

    @EventListener(Update.class)
    public void onUpdate(Update update) {
        log.info(update.toString());
    }
}

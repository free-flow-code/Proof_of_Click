INSERT INTO users (username, mail, hash_password, registration_date, referral_link, referer, blocks_balance, blocks_per_sec, blocks_per_click, improvements, telegram_id, last_update_time) VALUES 
('user1', 'user1@test.com', 'df546fg45g4t', '2024-06-01', 'REFlink1', null, 1.000, 0.002, 0.001, null, null, null),
('user2', 'user2@test.com', 'dfhjgjuj6j75g4t', '2024-06-02', 'REFlink2', null, 2.000, 0.002, 0.001, null, null, null),
('user3', 'user3@test.com', 'df54908plok5g4t', '2024-06-03', 'REFlink3', null, 0.050, 0.000, 0.002, null, null, null),
('user4', 'user4@test.com', 'df54dve4t', '2024-06-04', 'REFlink4', null, 1.900, 0.000, 0.002, null, null, null),
('user5', 'user5@test.com', 'df546fg23fet', '2024-06-05', 'REFlink5', null, 0.900, 0.000, 0.001, null, null, null),
('user6', 'user6@test.com', '45yhfg45g4t', '2024-06-06', 'REFlink6', null, 0.888, 0.000, 0.001, null, null, null);

INSERT INTO improvements (user_id, name, purchase_date, level, redis_key, image_id) VALUES
(43, 'Автокликер', '2024-06-02', 2, 'autoclicker', null),
(44, 'Автокликер', '2024-06-03', 2, 'autoclicker', null),
(45, 'Умножитель', '2024-06-04', 2, 'multiplier', null),
(46, 'Умножитель', '2024-06-05', 2, 'multiplier', null);

UPDATE users SET improvements = 9 WHERE id = 43;
UPDATE users SET improvements = 10, referer = 43 WHERE id = 44;
UPDATE users SET improvements = 11, referer = 43 WHERE id = 45;
UPDATE users SET improvements = 12, referer = 45 WHERE id = 46;
UPDATE users SET referer = 45 WHERE id = 47;

INSERT INTO game_items (user_id, name, date_at_mine, redis_key, image_id) VALUES 
(43, 'Полиморфный блок', '2024-06-10', 'polymorphic_block', null),
(44, 'Полиморфный блок', '2024-06-11', 'polymorphic_block', null);

INSERT INTO lots (user_id, date_at_create, expiration_date, game_item_id, start_price, best_price, best_price_user_id) VALUES
(43, '2024-06-15', '2024-10-15', 1, 100.00, 150.00, 47),
(44, '2024-06-20', '2024-10-20', 2, 110.00, 150.00, 48);

INSERT INTO notifications (user_id, text, send_date) VALUES 
(43, 'Поздравляем с добытым блоком!', '2024-06-10'),
(44, 'Поздравляем с добытым блоком!', '2024-06-11');

/* Возможно придется подставлять другие id для пользователей, предметов, улучшений */
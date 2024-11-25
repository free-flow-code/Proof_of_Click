# Lua-скрипт для подсчета суммы балансов всех пользователей (сгенерированных блоков)
total_sum_script = f"""
local sum = 0
local zset_key = KEYS[1]
local items = redis.call('ZRANGE', zset_key, 0, -1, 'WITHSCORES')
for i = 2, #items, 2 do
    sum = sum + tonumber(items[i])
end
return sum
"""
# Lua-скрипт для получения топ N пользователей по размеру баланса
top_users_script = """
local zset_key = KEYS[1]
local top_n = tonumber(ARGV[1])

local top_users = redis.call('ZREVRANGE', zset_key, 0, top_n - 1, 'WITHSCORES')
local result = {}

for i = 1, #top_users, 2 do
    local username = top_users[i]
    local balance = top_users[i + 1]
    table.insert(result, {username, balance})
end

return result
"""
# Lua-скрипт для пересчета баланса пользователей в зависимости от значения автокликера,
# умножителя и времени с последнего обновления.
recalculate_user_data_script = """
local users_keys = cjson.decode(ARGV[1])
local current_time = tonumber(ARGV[2])
local balances_key = ARGV[3]
local user_clicks = {}

-- Обрабатываем каждый ключ
for _, key in ipairs(users_keys) do
    local user_data = redis.call('HGETALL', key)

    -- Логика обработки данных
    local balance = 0
    local clicks_per_sec = 0
    local blocks_per_click = 0
    local last_update_time = 0
    local username = nil

    -- Проходим по элементам user_data (список ключ-значение)
    for i = 1, #user_data, 2 do
        local field = user_data[i]
        local value = user_data[i + 1]

        if field == "blocks_balance" then
            balance = tonumber(value) or 0
        elseif field == "clicks_per_sec" then
            clicks_per_sec = tonumber(value) or 0
        elseif field == "blocks_per_click" then
            blocks_per_click = tonumber(value) or 0
        elseif field == "last_update_time" then
            last_update_time = tonumber(value) or 0
        elseif field == "username" then
            username = value
        end
    end

    -- Логика обработки данных
    local timedelta = current_time - last_update_time
    local clicks = clicks_per_sec * timedelta

    -- Обновляем Redis
    redis.call('HMSET', key, 'blocks_balance', balance + clicks * blocks_per_click, 'last_update_time', current_time)
    redis.call("ZADD", balances_key, balance, username)

    -- Добавляем результат в список
    user_clicks[key] = clicks
end

return cjson.encode(user_clicks)
"""

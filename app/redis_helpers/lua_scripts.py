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

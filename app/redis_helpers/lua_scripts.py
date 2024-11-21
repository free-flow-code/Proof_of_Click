from app.config import settings

# Lua-скрипт для подсчета суммы балансов всех пользователей (сгенерированных блоков)
total_sum_script = f"""
local sum = 0
local items = redis.call('ZRANGE', 'users_balances:{settings.REDIS_NODE_TAG_3}, 0, -1, 'WITHSCORES')
for i = 2, #items, 2 do
    sum = sum + tonumber(items[i])
end
return sum
"""

# Практикум по робототехнике на ROS 2 (НГУ)

Репозиторий содержит материалы практических заданий курса робототехники.

## Практика 01 (ПР01): Окружение и граф ROS 2

### Воспроизведение эксперимента

1. **Подготовка окружения:**
   - Запуск рабочего контейнера ROS 2 (Lyrical, Ubuntu 26.04).
   - В терминалах настраивается окружение:
     ```bash
     source /opt/ros/lyrical/setup.bash
     ```

2. **Шаг 1: Запуск исправного графа (домен 16):**
   - Терминал A: `export ROS_DOMAIN_ID=16 && ros2 run turtlesim turtlesim_node`
   - Терминал B: `export ROS_DOMAIN_ID=16 && ros2 run turtlesim turtle_teleop_key`
   - Терминал C: наблюдение и замеры:
     ```bash
     export ROS_DOMAIN_ID=16
     ros2 node list --no-daemon --spin-time 2
     ros2 topic list -t
     ros2 node info /turtlesim
     POSE_TYPE=$(ros2 topic type /turtle1/pose)
     ros2 topic echo /turtle1/pose --once
     ros2 topic hz /turtle1/pose
     ```

3. **Шаг 2: Воспроизведение сбоя (разрыв домена):**
   - Перевод управления в домен 17 (Терминал B):
     ```bash
     export ROS_DOMAIN_ID=17 && ros2 run turtlesim turtle_teleop_key
     ```
   - Наблюдение в домене 17 (Терминал C):
     ```bash
     export ROS_DOMAIN_ID=17
     ros2 node list --no-daemon --spin-time 2
     timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once
     printf 'exit=%s\n' "$?"
     ```
     Ожидается код возврата `124` (таймаут ожидания сообщений).

4. **Шаг 3: Восстановление связи:**
   - Возврат управления в домен 16 (Терминал B):
     ```bash
     export ROS_DOMAIN_ID=16 && ros2 run turtlesim turtle_teleop_key
     ```
   - Проверка в домене 16 (Терминал C):
     ```bash
     export ROS_DOMAIN_ID=16
     timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once
     printf 'exit=%s\n' "$?"
     ```
     Ожидается код возврата `0` и вывод сообщения позы.

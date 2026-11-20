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

## Практика 02 (ПР02): пакет turtle_bringup и launch

Пакет `src/turtle_bringup` содержит launch-файл `launch/sim.launch.py`, который запускает узел `turtlesim`. Корень workspace — корень репозитория.

### Воспроизведение эксперимента

1. **Сборка и подключение пакета:**
   ```bash
   source /opt/ros/lyrical/setup.bash
   colcon build --symlink-install --packages-select turtle_bringup
   source install/setup.bash
   ros2 pkg prefix turtle_bringup
   ```

2. **Запуск (терминал A):**
   ```bash
   export ROS_DOMAIN_ID=16
   export DISPLAY=:1
   ros2 launch turtle_bringup sim.launch.py
   ```
   Проверка графа (терминал C): `ros2 node list --no-daemon --spin-time 2` выводит `/turtlesim`. Остановка: Ctrl+C в терминале A.

3. **Отправка команды:**
   ```bash
   ros2 topic echo /turtle1/pose --once
   ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist '{linear: {x: 1.0}, angular: {z: 0.5}}'
   ros2 topic echo /turtle1/pose --once
   ```
   Черепаха проезжает вперёд с поворотом влево и останавливается.

4. **Воспроизведение сбоя (неверное имя топика):**
   - Терминал B:
     ```bash
     ros2 topic pub --rate 1 --wait-matching-subscriptions 0 /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 1.0}, angular: {z: 0.5}}'
     ```
   - Терминал C:
     ```bash
     ros2 topic info /cmd_vel --verbose
     ros2 topic info /turtle1/cmd_vel --verbose
     ros2 topic echo /turtle1/pose --once
     ```
     У `/cmd_vel`: 1 издатель, 0 подписчиков; у `/turtle1/cmd_vel`: 0 издателей, 1 подписчик (`turtlesim`). Черепаха стоит, скорости 0.0.

5. **Исправление:** остановить издателя (Ctrl+C) и запустить ту же команду, изменив только имя топика:
   ```bash
   ros2 topic pub --rate 1 --wait-matching-subscriptions 0 /turtle1/cmd_vel geometry_msgs/msg/Twist '{linear: {x: 1.0}, angular: {z: 0.5}}'
   ros2 topic info /turtle1/cmd_vel --verbose
   ros2 topic echo /turtle1/pose --once
   ```
   Publisher count 1, Subscription count 1, в позе `linear_velocity: 1.0`, `angular_velocity: 0.5`, черепаха едет.

## Практика 04 (ПР04). Параметры движения

В контейнере Lyrical из корня репозитория соберите оба пакета.

```bash
source /opt/ros/lyrical/setup.bash
colcon build --symlink-install --packages-select turtle_bringup patrol
```

В каждом новом терминале подключите базовую ROS, затем
`source install/setup.bash` и `export ROS_DOMAIN_ID=16`.
В первом терминале запустите `DISPLAY=:1 ros2 launch turtle_bringup sim.launch.py`,
во втором — `ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel`.

В третьем терминале измерьте частоту топика до изменения, после установки
`5.0` Гц и после отклонения `0.0` Гц.

```bash
timeout -s INT 6s ros2 topic hz /turtle1/cmd_vel
ros2 param set /patrol publish_hz 5.0
timeout -s INT 6s ros2 topic hz /turtle1/cmd_vel
timeout 8s ros2 param set /patrol publish_hz 0.0
ros2 param get /patrol publish_hz
timeout -s INT 6s ros2 topic hz /turtle1/cmd_vel
```

Открытые тесты и проверка комплекта сдачи выполняются из корня репозитория.

```bash
(cd src/patrol && python3 -m pytest test)
python3 .course-kit/v1/tools/check_practice.py PR04 --submission .
```

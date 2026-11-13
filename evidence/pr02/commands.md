# ПР02: команды и наблюдения

Среда: контейнер `tiryoh/ros2-desktop-vnc:lyrical-20260906T0836`, ROS 2 Lyrical,
`ROS_DOMAIN_ID=16`. Корень workspace — корень репозитория, в контейнере это
`/home/ubuntu/robotics`.

## 1. Команды Linux

### `printenv AMENT_PREFIX_PATH`

Назначение: прочитать переменную окружения текущего терминала. В ней список папок,
в которых `ros2` ищет установленные пакеты.

Результат до подключения своего workspace:

```text
/opt/ros/lyrical
```

Результат после `source install/setup.bash`:

```text
/home/ubuntu/robotics/install/turtle_bringup:/opt/ros/lyrical
```

### `source install/setup.bash`

Назначение: выполнить скрипт, который создал `colcon`, в текущем терминале. Скрипт
добавляет папку `install` моего workspace в `AMENT_PREFIX_PATH`.

Результат: до этой команды `ros2 pkg prefix turtle_bringup` отвечал
`Package not found`, после неё:

```text
/home/ubuntu/robotics/install/turtle_bringup
```

### `ls install/turtle_bringup/share/turtle_bringup/launch`

Назначение: показать содержимое каталога. Здесь проверяю, что launch-файл попал
из `src` в установленный пакет.

Результат:

```text
sim.launch.py
```

### Чем `>` отличается от `|`

`>` записывает вывод команды в файл, прежнее содержимое файла заменяется.
`|` передаёт вывод одной команды на вход другой команде.

Пример из этой работы:

```bash
colcon build --symlink-install --packages-select turtle_bringup 2>&1 | tee evidence/pr02/build.txt
```

`2>&1` направляет сообщения об ошибках туда же, куда идёт обычный вывод. `|` передаёт
всё это программе `tee`, а она одновременно печатает текст на экран и пишет его в файл.
С `> evidence/pr02/build.txt` лог попал бы только в файл, на экране ничего бы не было.

### Чем `source` отличается от запуска новой программы

`source файл` выполняет команды из файла в текущем терминале, поэтому переменные,
которые он выставил, остаются в этом терминале. Если запустить тот же файл как
программу (`bash install/setup.bash`), он выполнится в отдельном процессе, изменит
окружение только у себя и завершится, а в моём терминале ничего не изменится.
Подтверждение: `AMENT_PREFIX_PATH` изменился именно в том терминале, где был выполнен
`source` (вывод выше).

## 2. Сборка и обнаружение пакета

Логи сборки: `build-empty.txt` (пустой пакет, без launch-файла) и `build.txt`
(итоговая сборка с launch-файлом).

```bash
colcon build --symlink-install --packages-select turtle_bringup
```

```text
Starting >>> turtle_bringup
Finished <<< turtle_bringup [2.44s]

Summary: 1 package finished [2.73s]
```

После сборки и `source install/setup.bash` пакет находится, launch-файл установлен
(выводы в разделе 1). При этом нод в графе нет:

```bash
ros2 node list --no-daemon --spin-time 2
```

Вывод пустой. Сборка и `source` только делают пакет видимым для `ros2`,
процессы они не запускают.

## 3. Запуск и остановка launch

Терминал A:

```bash
source /opt/ros/lyrical/setup.bash
cd /home/ubuntu/robotics
source install/setup.bash
export ROS_DOMAIN_ID=16
export DISPLAY=:1
ros2 launch turtle_bringup sim.launch.py
```

`export DISPLAY=:1` нужен, потому что терминал открыт через `docker exec`: без него
turtlesim не знает, на каком экране рисовать окно, и падает с
`could not connect to display`.

Результат: на рабочем столе контейнера открылось одно окно turtlesim.

Проверка графа в терминале C:

```bash
ros2 node list --no-daemon --spin-time 2
```

```text
/turtlesim
```

Остановка: Ctrl+C в терминале A. Повтор той же проверки в C даёт пустой вывод:
launch завершил процесс turtlesim, который сам запустил.

## 4. Команда и движение

Launch работает в A, teleop не запущен. Поза до команды:

```bash
ros2 topic echo /turtle1/pose --once
```

```text
x: 6.509308815002441
y: 5.796990871429443
theta: 0.5040000081062317
linear_velocity: 0.0
angular_velocity: 0.0
```

Команда:

```bash
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

```text
publisher: beginning loop
publishing #1: geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=1.0, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0.0, y=0.0, z=0.5))
```

Ожидание: черепаха проедет вперёд примерно на 1 с поворотом влево (против часовой
стрелки), `theta` вырастет примерно на 0.5.

Поза после:

```text
x: 7.232236862182617
y: 6.4840989112854
theta: 1.0080000162124634
linear_velocity: 0.0
angular_velocity: 0.0
```

Факт: `x` вырос на 0.72, `y` на 0.69 (черепаха уже была повёрнута на 0.5 рад, поэтому
ехала вправо-вверх), пройденное расстояние около 1, `theta` вырос на 0.504.
Скорости снова 0.0: одна публикация не задаёт бесконечное движение, без новых команд
turtlesim останавливается.

## 5. Сбой в имени топика и исправление

### Сбой

Терминал B, тот же Twist, но в топик `/cmd_vel`:

```bash
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

Издатель печатает `publishing #1`, `#2`, ..., черепаха стоит. Пока он работает,
в терминале C (блок `QoS profile` из вывода опущен):

```bash
ros2 topic info /cmd_vel --verbose
```

```text
Type: geometry_msgs/msg/Twist

Publisher count: 1

Node name: _ros2cli_1225174
Node namespace: /
Topic type: geometry_msgs/msg/Twist
Endpoint type: PUBLISHER

Subscription count: 0
```

```bash
ros2 topic info /turtle1/cmd_vel --verbose
```

```text
Type: geometry_msgs/msg/Twist

Publisher count: 0

Subscription count: 1

Node name: turtlesim
Node namespace: /
Topic type: geometry_msgs/msg/Twist
Endpoint type: SUBSCRIPTION
```

```bash
ros2 topic echo /turtle1/pose --once
```

```text
x: 7.232236862182617
y: 6.4840989112854
theta: 1.0080000162124634
linear_velocity: 0.0
angular_velocity: 0.0
```

Поза та же, что после команды из раздела 4, скорости 0.0: сообщения публикуются,
но черепаха их не получает.

### Исправление

В B остановил издателя (Ctrl+C) и запустил ту же команду, изменив только имя топика:

```bash
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 /turtle1/cmd_vel geometry_msgs/msg/Twist '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

В C:

```bash
ros2 topic info /cmd_vel --verbose
```

```text
Unknown topic '/cmd_vel'
```

```bash
ros2 topic info /turtle1/cmd_vel --verbose
```

```text
Type: geometry_msgs/msg/Twist

Publisher count: 1

Node name: _ros2cli_1247528
Node namespace: /
Topic type: geometry_msgs/msg/Twist
Endpoint type: PUBLISHER

Subscription count: 1

Node name: turtlesim
Node namespace: /
Topic type: geometry_msgs/msg/Twist
Endpoint type: SUBSCRIPTION
```

```bash
ros2 topic echo /turtle1/pose --once
```

```text
x: 4.401844024658203
y: 9.191462516784668
theta: -2.542370557785034
linear_velocity: 1.0
angular_velocity: 0.5
```

Черепаха едет по кругу: скорости равны отправленным (1.0 и 0.5), поза меняется.
После наблюдения издатель остановлен, черепаха остановилась.

### Сравнение

| Состояние | `/cmd_vel` | `/turtle1/cmd_vel` | Черепаха |
|---|---|---|---|
| До (раздел 4) | топика нет | издатель на время команды, подписчик `turtlesim` | проехала и остановилась |
| Сбой | 1 издатель, 0 подписчиков | 0 издателей, 1 подписчик `turtlesim` | стоит, скорости 0.0 |
| После | топика нет (`Unknown topic`) | 1 издатель, 1 подписчик `turtlesim` | едет, скорости 1.0 и 0.5 |

### Почему правильного типа недостаточно

В сбойном состоянии тип сообщения был правильный (`geometry_msgs/msg/Twist`), домен
тот же, издатель был виден в графе. Но издатель и подписчик соединяются только на
одном и том же топике, то есть при совпадении полного имени. Turtlesim подписан на
`/turtle1/cmd_vel`, а сообщения шли в `/cmd_vel`. Для ROS это два разных топика,
никак не связанных между собой. Тип описывает содержимое сообщения, а куда оно
попадёт, определяет имя топика.

Обнаружение и доставка здесь разошлись. Обнаружение работало: обе ноды были в одном
домене и видны через CLI. Доставки не было: на топике издателя не было ни одного
подписчика. Исправлено только имя топика, тип, данные и домен не менялись, после
этого команда дошла.

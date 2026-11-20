# ПР04. Параметры движения

## Сбой при отключённой проверке частоты

Ветка `codex/pr04-zero-frequency`, коммит `10b0c7e`. В `check_parameters`
временно пропущена проверка `publish_hz`. После сборки нода запущена командой
`ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel`.

```console
$ ros2 param get /patrol publish_hz
$ timeout 8s ros2 param set /patrol publish_hz 0.0
Double value is: 10.0
exit=124
```

Последние строки из терминала ноды:

```text
  File "/home/ubuntu/robotics/build/patrol/patrol/patrol.py", line 71, in apply_parameters
    1.0 / frequency, self.on_timer, autostart=False)
    ~~~~^~~~~~~~~~~
ZeroDivisionError: division by zero
[ros2run]: Process exited with failure 1
```

ROS принял нулевое значение и вызвал `apply_parameters`. При вычислении
периода произошло деление на ноль, и процесс ноды завершился с кодом 1.
Клиент ожидал ответа до таймаута, поэтому `timeout` вернул код 124.

## Проверка после восстановления валидации

Замеры выполнены в контейнере Lyrical в домене 16. Каждая команда
`ros2 topic hz /turtle1/cmd_vel` выполнялась с ограничением `timeout -s INT 6s`.

```console
$ ros2 topic hz /turtle1/cmd_vel — исходная частота
WARNING: topic [/turtle1/cmd_vel] does not appear to be published yet
average rate: 9.997
	min: 0.093s max: 0.106s std dev: 0.00370s window: 9
average rate: 10.002
	min: 0.093s max: 0.106s std dev: 0.00318s window: 19
$ ros2 param set /patrol publish_hz 5.0
Set parameter successful
$ ros2 topic hz /turtle1/cmd_vel — после 5.0
average rate: 5.084
	min: 0.187s max: 0.205s std dev: 0.00674s window: 4
average rate: 5.026
	min: 0.187s max: 0.209s std dev: 0.00640s window: 9
average rate: 5.021
	min: 0.187s max: 0.209s std dev: 0.00533s window: 14
average rate: 5.015
	min: 0.187s max: 0.209s std dev: 0.00472s window: 19
$ timeout 8s ros2 param set /patrol publish_hz 0.0
Setting parameter failed: publish_hz must be finite and in [1.0, 30.0]
$ ros2 param get /patrol publish_hz
Double value is: 5.0
$ ros2 topic hz /turtle1/cmd_vel — после отказа
WARNING: topic [/turtle1/cmd_vel] does not appear to be published yet
average rate: 4.920
	min: 0.125s max: 0.275s std dev: 0.05348s window: 4
average rate: 4.962
	min: 0.125s max: 0.275s std dev: 0.03724s window: 9
```

Последние средние значения в трёх замерах: 10.002, 5.015 и 4.962 Гц.
Изменение на 5.0 Гц принято. Запрос с 0.0 отклонён, значение параметра
по-прежнему 5.0 и поток команд продолжается с частотой около 5 Гц.

Изменение скорости также проверено вручную: после команды
`ros2 param set /patrol linear_speed 0.7` получено `Set parameter successful`.
Команда `ros2 topic echo /turtle1/cmd_vel --once` показала `linear.x: 0.7`
и `angular.z: 0.3`.

## Сервис и действие turtlesim

```console
$ ros2 service call /clear std_srvs/srv/Empty '{}'
waiting for service to become available...
requester: making request: std_srvs.srv.Empty_Request()

response:
std_srvs.srv.Empty_Response()

$ ros2 action list -t
/turtle1/rotate_absolute [turtlesim_msgs/action/RotateAbsolute]
```

Запрос к сервису `/clear` просит стереть след и получает один ответ.
Цель действия `/turtle1/rotate_absolute` задаёт угол поворота, а во время
выполнения клиент может получать обратную связь и запросить отмену.

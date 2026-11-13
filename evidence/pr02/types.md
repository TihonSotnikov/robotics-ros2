# ПР02: топики и типы сообщений

## Два основных топика

| Топик | Тип | Кто публикует | Кто подписан | Назначение |
|---|---|---|---|---|
| `/turtle1/cmd_vel` | `geometry_msgs/msg/Twist` | `ros2 topic pub` (в ПР01 — teleop) | `/turtlesim` | команда скорости для черепахи |
| `/turtle1/pose` | `turtlesim_msgs/msg/Pose` | `/turtlesim` | `ros2 topic echo` на время команды | текущее положение и скорости черепахи |

Тип позы взят из вывода `ros2 topic type /turtle1/pose` в моей среде (Lyrical).

## Поля Twist

```bash
ros2 interface show geometry_msgs/msg/Twist
```

```text
# This expresses velocity in free space broken into its linear and angular parts.

Vector3  linear
        float64 x
        float64 y
        float64 z
Vector3  angular
        float64 x
        float64 y
        float64 z
```

Twist — это скорость, разложенная на две части по три числа:

- `linear` — линейная скорость по осям x, y, z. `linear.x` — скорость вперёд,
  по направлению, куда смотрит черепаха.
- `angular` — угловая скорость вокруг осей x, y, z, в радианах в секунду.
  `angular.z` — поворот на плоскости; положительное значение поворачивает
  против часовой стрелки.

В работе отправлялось `{linear: {x: 1.0}, angular: {z: 0.5}}`: вперёд со скоростью 1.0
и поворот влево 0.5 рад/с. Остальные поля не указаны и равны 0.0. Черепаха движется
на плоскости, поэтому ей и нужны только движение вперёд и поворот вокруг вертикальной
оси.

## Поля Pose

По выводу `ros2 topic echo /turtle1/pose --once`:

- `x`, `y` — координаты черепахи в окне;
- `theta` — угол, куда она смотрит, в радианах;
- `linear_velocity`, `angular_velocity` — текущие скорости; 0.0, когда черепаха стоит.

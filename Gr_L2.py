"""Пакеты"""
import librosa
import os
import numpy as np
from graphics import *
from shapely.geometry.polygon import Polygon as Pol
from shapely.geometry import Point as Po


class MyPoint(object):
    """Точка - """

    def __init__(self, x, y=0, z=0):
        if type(x) is list:
            self.x = x[0]
            self.y = x[1]
            self.z = x[2]
        else:
            self.x = x
            self.y = y
            self.z = z


class MyPolygon(object):
    """Полигон (точки, цвет)"""

    def __init__(self, points, color=None):
        if color is None:
            self.color = color_rgb(255, 0, 0)
        else:
            self.color = color

        self.points = []
        for point in points:
            if type(point) is MyPoint:
                self.points.append(point)
            else:
                self.points.append(MyPoint(point))


def is_inside(_point, _polygon):
    """
    Функция возращает True если координаты (x, y) внутри полигона
    обозначеного списком вершин [(x1, x2), ... , (xN, yN)]
    """

    x = _point.x  # x
    y = _point.y  # y

    points = _polygon.points  # список вершин полигона
    num_points = len(points)  # количество вершин полигона
    inside_flag = False  # флаг вхождения

    polygon_x, polygon_y = [points[0].x, points[0].y]  # начальные точки полигона

    for i in range(1, num_points + 1):
        point2x, point2y = [points[i % num_points].x, points[i % num_points].y]

        if y > min(polygon_y, point2y):
            if y <= max(polygon_y, point2y):
                if x <= max(polygon_x, point2x):
                    x_inters = 0
                    if polygon_y != point2y:
                        x_inters = (y - polygon_y) * (point2x - polygon_x) / (point2y - polygon_y) + polygon_x

                    if polygon_x == point2x or x <= x_inters:
                        inside_flag = not inside_flag

        polygon_x, polygon_y = point2x, point2y
    return inside_flag


def points_in_polygon(_points, _polygon):
    """Количество точек в полигоне"""

    num_result = 0

    for point in _points:
        if is_inside(point, _polygon):
            num_result += 1

    return num_result


def split_check(_point_f, _point_s, _polygons, _win, _background=None):
    """Проверка разбиения"""

    if _point_s[0] - _point_f[0] > 1:
        dx = _point_s[0] - _point_f[0]
        dy = _point_s[1] - _point_f[1]

        dx2 = int(dx / 2.)
        dy2 = int(dy / 2.)

        # Левый-верхний квадрат
        check(_point_f, [_point_f[0] + dx2, _point_f[1] + dy2], _polygons, _win, _background)

        # Правый-верхний квадрат
        check([_point_f[0] + dx2, _point_f[1]], [_point_s[0], _point_f[1] + dy2], _polygons, _win, _background)

        # Правый-нижний квадрат
        check([_point_f[0] + dx2, _point_f[1] + dy2], _point_s, _polygons, _win, _background)

        # Левый-нижний квадрат
        check([_point_f[0], _point_f[1] + dy2], [_point_f[0] + dx2, _point_s[1]], _polygons, _win, _background)

    else:
        # Левый-верхний квадрат
        check(_point_f, _point_f, _polygons, _win, _background)

        # Правый-верхний квадрат
        check([_point_s[0], _point_f[1]], [_point_s[0], _point_f[1]], _polygons, _win, _background)

        # Правый-нижний квадрат
        check(_point_s, _point_s, _polygons, _win, _background)

        # Левый-нижний квадрат
        check([_point_f[0], _point_s[1]], [_point_f[0], _point_s[1]], _polygons, _win, _background)


def get_z_coordinate(_point, _polygon):
    """Получаем координату z"""

    m1 = _polygon.points[0]
    m2 = _polygon.points[1]
    m3 = _polygon.points[2]

    vec_f = [m2.x - m1.x, m2.y - m1.y, m2.z - m1.z]
    vec_s = [m3.x - m1.x, m3.y - m1.y, m3.z - m1.z]

    vec_n = [vec_f[1] * vec_s[2] - vec_f[2] * vec_s[1],
             vec_f[2] * vec_s[0] - vec_f[0] * vec_s[2],
             vec_f[0] * vec_s[1] - vec_f[1] * vec_s[0]]

    d = -m1.x * vec_n[0] - m1.y * vec_n[1] - m1.z * vec_n[2]

    vec = [[vec_n[0], _point[0]],
           [vec_n[1], _point[1]],
           [vec_n[2], 0]]

    sums = [0, 0]
    for i in range(3):
        sums[0] += vec[i][0] * vec_n[i]
        sums[1] += vec[i][1] * vec_n[i]

    sums[1] += d
    t = -sums[1] / sums[0]

    x = vec_n[0] * t + _point[0]
    y = vec_n[1] * t + _point[1]
    z = vec_n[2] * t + 0

    return x, y, z


def check(_point_f, _point_s, _polygons, _win, _background=None):
    """Основной алгоритм Варнока"""

    draw_borders = False

    # если не фона заливаем его цветом
    if _background is None:
        _background = color_rgb(255, 255, 0)

    # если точка одна, то проверям полигоны на её вхождение
    if _point_f[0] == _point_s[0]:
        max_z = -np.inf
        max_polygon = None

        # берем полигон
        for polygon in _polygons:
            # если точка входит в полигон
            if is_inside(MyPoint(_point_f[0], _point_f[1]), polygon):
                # получаем z
                z = get_z_coordinate(_point_f, polygon)[2]
                # если z больше запоминаем новые максимальные значения
                if z > max_z:
                    max_polygon = polygon
                    max_z = z

        # если нет полигона
        if max_polygon is None:
            # красим фоном
            _win.plotPixel(_point_f[0], _point_f[1], _background)
        else:
            # красим цветом полигона
            _win.plotPixel(_point_f[0], _point_s[1], max_polygon.color)
        return

    # квадрат
    rec = MyPolygon([MyPoint(_point_f[0], _point_f[1], 0),
                     MyPoint(_point_f[0], _point_s[1], 0),
                     MyPoint(_point_s[0], _point_s[1], 0),
                     MyPoint(_point_s[0], _point_f[1], 0)])

    # Считаем сколько вершин квадрата входят в каждый полигон
    # и сколько вершин каждого полигона входят в квадрат
    poly_in_rec = []
    rec_in_polygon = []
    for polygon in _polygons:
        rec_in_polygon.append(points_in_polygon(rec.points, polygon))
        poly_in_rec.append(points_in_polygon(polygon.points, rec))

    poly_in_rec = np.array(poly_in_rec)
    rec_in_polygon = np.array(rec_in_polygon)

    # Если в квадрат не внутри никакого полигона и внутри квадрата нет полигона,
    # то зарисовываем квадрат фоном
    if (poly_in_rec.max() == 0) and (rec_in_polygon.max() == 0):
        rect = Rectangle(Point(_point_f[0], _point_f[1]), Point(_point_s[0] - 1, _point_s[1] - 1))
        rect.setFill(_background)
        if not draw_borders:
            rect.setOutline(_background)
        rect.draw(_win)
        return

    # Если внутри квадрата есть хоть 1 вершина полигона, разбиваем квадрат
    split = False
    for p in poly_in_rec:
        if p > 0:
            split = True
    if split:
        split_check(_point_f, _point_s, polygons, win, _background)
        return

    if len(polygons[np.where(rec_in_polygon > 0)]) > 1:
        split_check(_point_f, _point_s, polygons, win, _background)
        return

    # Выбираем среди полигонов те, в которые квадрат входит полностью
    # если таких больше 1, то разбиваем квадрат
    rec_inside_polygon = _polygons[np.where(rec_in_polygon == 4)]
    if len(rec_inside_polygon) > 0:
        rect = Rectangle(Point(_point_f[0], _point_f[1]), Point(_point_s[0] - 1, _point_s[1] - 1))
        rect.setFill(rec_inside_polygon[0].color)
        if not draw_borders:
            rect.setOutline(rec_inside_polygon[0].color)
        rect.draw(_win)
        return

    # Если хотябы одна вершина квадрата входит в какой-то полигон, то разбиваем квадрат
    split = False
    for p in rec_in_polygon:
        if p > 0:
            split = True
    if split:
        split_check(_point_f, _point_s, _polygons, _win, _background)
        return


if __name__ == '__main__':
    polygons = []
    win = GraphWin("MyWin", 256, 256)
    polygons.append(MyPolygon([[50, 150, 0], [150, 200, 00], [150, 100, 60]], color_rgb(126, 20, 135)))
    polygons.append(MyPolygon([[50, 100, 0], [10, 200, 100], [200, 150, 0]], color_rgb(18, 162, 184)))
    polygons.append(MyPolygon([[50, 100, 8], [100, 256, 100], [150, 150, 6]], color_rgb(180, 162, 184)))

    polygons = np.array(polygons)

    # Polygon([Point(100, 100), Point(150, 200), Point(50, 200)]).draw(win)
    # Polygon([Point(150, 100), Point(200, 200), Point(250, 100)]).draw(win)

    check([0, 0], [256, 256], polygons, win, color_rgb(255, 255, 255))
    # Polygon([Point(100, 100), Point(150, 200), Point(50, 200)]).draw(win)
    # Polygon([Point(150, 100), Point(200, 200), Point(250, 100)]).draw(win)

    win.getMouse()
    win.close()

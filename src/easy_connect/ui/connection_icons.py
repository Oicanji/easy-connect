from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap


ICON_COLOR = "#2f9e8f"
DEFAULT_ICON = "server"
_VIEW = 24.0


def _pen(painter: QPainter) -> None:
    pen = QPen(QColor(ICON_COLOR))
    pen.setWidthF(1.7)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)


def _box(painter: QPainter, x: float, y: float, w: float, h: float, r: float = 2) -> None:
    painter.drawRoundedRect(QRectF(x, y, w, h), r, r)


def _line(painter: QPainter, x1: float, y1: float, x2: float, y2: float) -> None:
    painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))


def _dot(painter: QPainter, x: float, y: float, r: float = 1.15) -> None:
    painter.setBrush(QColor(ICON_COLOR))
    painter.drawEllipse(QPointF(x, y), r, r)
    painter.setBrush(Qt.BrushStyle.NoBrush)


def _oval(painter: QPainter, x: float, y: float, w: float, h: float) -> None:
    painter.drawEllipse(QRectF(x, y, w, h))


def _server(p: QPainter) -> None:
    _box(p, 4, 3, 16, 6)
    _box(p, 4, 15, 16, 6)
    _dot(p, 7.2, 6)
    _dot(p, 7.2, 18)


def _monitor(p: QPainter) -> None:
    _box(p, 3, 4, 18, 12, 2)
    _line(p, 9, 16, 9, 19)
    _line(p, 15, 16, 15, 19)
    _line(p, 8, 19.5, 16, 19.5)


def _laptop(p: QPainter) -> None:
    _box(p, 5, 4, 14, 10, 1.5)
    _line(p, 3, 16, 21, 16)
    _line(p, 6, 16, 8, 14)
    _line(p, 18, 16, 16, 14)


def _terminal(p: QPainter) -> None:
    _box(p, 3, 4, 18, 16, 2)
    _line(p, 7, 9, 10, 12)
    _line(p, 10, 12, 7, 15)
    _line(p, 12, 15, 17, 15)


def _cloud(p: QPainter) -> None:
    _oval(p, 5, 9, 8, 7)
    _oval(p, 10, 6, 8, 8)
    _line(p, 7, 16, 17, 16)


def _database(p: QPainter) -> None:
    _oval(p, 5, 4, 14, 5)
    _line(p, 5, 6.5, 5, 17)
    _line(p, 19, 6.5, 19, 17)
    _oval(p, 5, 14.5, 14, 5)
    _line(p, 5, 11, 19, 11)


def _lock(p: QPainter) -> None:
    _box(p, 6, 10, 12, 9, 2)
    p.drawArc(QRectF(8, 5, 8, 8), 0, 180 * 16)


def _key(p: QPainter) -> None:
    _oval(p, 3, 8, 8, 8)
    _line(p, 11, 12, 20, 12)
    _line(p, 17, 12, 17, 15)
    _line(p, 14.5, 12, 14.5, 15)


def _shield(p: QPainter) -> None:
    p.drawPolygon(
        [
            QPointF(12, 3),
            QPointF(19, 6),
            QPointF(19, 12),
            QPointF(12, 21),
            QPointF(5, 12),
            QPointF(5, 6),
        ]
    )


def _globe(p: QPainter) -> None:
    _oval(p, 3, 3, 18, 18)
    _oval(p, 8, 3, 8, 18)
    _line(p, 3, 12, 21, 12)


def _network(p: QPainter) -> None:
    _dot(p, 12, 5, 1.6)
    _dot(p, 6, 18, 1.6)
    _dot(p, 18, 18, 1.6)
    _line(p, 12, 7, 6, 16)
    _line(p, 12, 7, 18, 16)
    _line(p, 8, 18, 16, 18)


def _folder(p: QPainter) -> None:
    _line(p, 4, 7, 10, 7)
    _line(p, 11, 7, 12.5, 9)
    _box(p, 4, 9, 16, 10, 2)


def _file(p: QPainter) -> None:
    p.drawPolygon(
        [
            QPointF(7, 3),
            QPointF(14, 3),
            QPointF(18, 7),
            QPointF(18, 21),
            QPointF(7, 21),
        ]
    )
    _line(p, 14, 3, 14, 7)
    _line(p, 14, 7, 18, 7)


def _package(p: QPainter) -> None:
    p.drawPolygon([QPointF(12, 3), QPointF(20, 7), QPointF(12, 11), QPointF(4, 7)])
    _line(p, 12, 11, 12, 21)
    _line(p, 4, 7, 4, 17)
    _line(p, 4, 17, 12, 21)
    _line(p, 20, 7, 20, 17)
    _line(p, 20, 17, 12, 21)


def _rocket(p: QPainter) -> None:
    p.drawPolygon([QPointF(12, 3), QPointF(16, 10), QPointF(16, 16), QPointF(8, 16), QPointF(8, 10)])
    _line(p, 8, 13, 5, 17)
    _line(p, 16, 13, 19, 17)
    _line(p, 10, 16, 12, 21)
    _line(p, 14, 16, 12, 21)
    _dot(p, 12, 12, 1.2)


def _wrench(p: QPainter) -> None:
    _oval(p, 13, 3, 7, 7)
    _line(p, 15.5, 9, 5, 19.5)
    _line(p, 5, 19.5, 7.5, 19.5)
    _line(p, 5, 17, 5, 19.5)


def _gear(p: QPainter) -> None:
    _oval(p, 8, 8, 8, 8)
    _oval(p, 10.2, 10.2, 3.6, 3.6)
    for x1, y1, x2, y2 in (
        (12, 2.5, 12, 6),
        (12, 18, 12, 21.5),
        (2.5, 12, 6, 12),
        (18, 12, 21.5, 12),
        (5.2, 5.2, 7.6, 7.6),
        (16.4, 16.4, 18.8, 18.8),
        (18.8, 5.2, 16.4, 7.6),
        (7.6, 16.4, 5.2, 18.8),
    ):
        _line(p, x1, y1, x2, y2)


def _user(p: QPainter) -> None:
    _oval(p, 8, 3.5, 8, 8)
    p.drawArc(QRectF(4, 13, 16, 12), 20 * 16, 140 * 16)


def _users(p: QPainter) -> None:
    _oval(p, 8, 4, 7, 7)
    p.drawArc(QRectF(5, 13, 14, 10), 20 * 16, 140 * 16)
    _oval(p, 3, 6, 5, 5)
    p.drawArc(QRectF(1, 14, 8, 8), 30 * 16, 120 * 16)


def _bug(p: QPainter) -> None:
    _oval(p, 7, 7, 10, 12)
    _line(p, 12, 7, 12, 19)
    _line(p, 7, 12, 4, 10)
    _line(p, 17, 12, 20, 10)
    _line(p, 7, 16, 4, 18)
    _line(p, 17, 16, 20, 18)
    _line(p, 10, 7, 8, 4)
    _line(p, 14, 7, 16, 4)


def _bolt(p: QPainter) -> None:
    p.drawPolygon(
        [
            QPointF(13, 2),
            QPointF(6, 13),
            QPointF(11, 13),
            QPointF(10, 22),
            QPointF(18, 10),
            QPointF(13, 10),
        ]
    )


def _wifi(p: QPainter) -> None:
    p.drawArc(QRectF(4, 6, 16, 12), 40 * 16, 100 * 16)
    p.drawArc(QRectF(7, 9, 10, 9), 40 * 16, 100 * 16)
    _dot(p, 12, 17, 1.3)


def _plug(p: QPainter) -> None:
    _line(p, 9, 3, 9, 8)
    _line(p, 15, 3, 15, 8)
    _box(p, 7, 8, 10, 6, 1.5)
    _line(p, 12, 14, 12, 21)


def _cpu(p: QPainter) -> None:
    _box(p, 7, 7, 10, 10, 1.5)
    for value in (9, 12, 15):
        _line(p, value, 3, value, 7)
        _line(p, value, 17, value, 21)
        _line(p, 3, value, 7, value)
        _line(p, 17, value, 21, value)


def _disk(p: QPainter) -> None:
    _oval(p, 3, 3, 18, 18)
    _oval(p, 8, 8, 8, 8)
    _dot(p, 12, 12, 1.2)


def _mail(p: QPainter) -> None:
    _box(p, 3, 5, 18, 14, 2)
    _line(p, 4, 6, 12, 12)
    _line(p, 20, 6, 12, 12)


def _bell(p: QPainter) -> None:
    p.drawArc(QRectF(6, 4, 12, 12), 0, 180 * 16)
    _line(p, 6, 10, 6, 15)
    _line(p, 18, 10, 18, 15)
    _line(p, 5, 15, 19, 15)
    _dot(p, 12, 18.5, 1.3)


def _search(p: QPainter) -> None:
    _oval(p, 4, 4, 11, 11)
    _line(p, 13.5, 13.5, 20, 20)


def _chart(p: QPainter) -> None:
    _line(p, 4, 20, 4, 4)
    _line(p, 4, 20, 20, 20)
    _line(p, 7, 15, 11, 11)
    _line(p, 11, 11, 14, 14)
    _line(p, 14, 14, 20, 6)


def _home(p: QPainter) -> None:
    p.drawPolygon([QPointF(3, 11), QPointF(12, 4), QPointF(21, 11)])
    _box(p, 6, 11, 12, 9, 1)


def _building(p: QPainter) -> None:
    _box(p, 5, 3, 14, 18, 1)
    for x in (8, 12, 16):
        for y in (6, 10, 14):
            _dot(p, x, y, 0.7)


def _star(p: QPainter) -> None:
    p.drawPolygon(
        [
            QPointF(12, 3),
            QPointF(14.4, 9),
            QPointF(21, 9.2),
            QPointF(15.8, 13.2),
            QPointF(17.6, 20),
            QPointF(12, 16.2),
            QPointF(6.4, 20),
            QPointF(8.2, 13.2),
            QPointF(3, 9.2),
            QPointF(9.6, 9),
        ]
    )


def _heart(p: QPainter) -> None:
    p.drawArc(QRectF(4, 5, 8, 8), 0, 220 * 16)
    p.drawArc(QRectF(12, 5, 8, 8), -40 * 16, 220 * 16)
    _line(p, 5.2, 10.5, 12, 19)
    _line(p, 18.8, 10.5, 12, 19)


def _check(p: QPainter) -> None:
    _line(p, 4, 12, 9, 18)
    _line(p, 9, 18, 20, 6)


def _alert(p: QPainter) -> None:
    p.drawPolygon([QPointF(12, 3), QPointF(21, 20), QPointF(3, 20)])
    _line(p, 12, 9, 12, 14)
    _dot(p, 12, 17, 0.9)


def _clock(p: QPainter) -> None:
    _oval(p, 3, 3, 18, 18)
    _line(p, 12, 7, 12, 12)
    _line(p, 12, 12, 16, 14)


def _calendar(p: QPainter) -> None:
    _box(p, 4, 5, 16, 15, 2)
    _line(p, 4, 9, 20, 9)
    _line(p, 8, 3, 8, 7)
    _line(p, 16, 3, 16, 7)


def _download(p: QPainter) -> None:
    _line(p, 12, 4, 12, 15)
    _line(p, 7, 11, 12, 16)
    _line(p, 17, 11, 12, 16)
    _line(p, 5, 19, 19, 19)


def _upload(p: QPainter) -> None:
    _line(p, 12, 16, 12, 5)
    _line(p, 7, 9, 12, 4)
    _line(p, 17, 9, 12, 4)
    _line(p, 5, 19, 19, 19)


def _link(p: QPainter) -> None:
    p.drawArc(QRectF(8, 4, 10, 8), 0, 180 * 16)
    _line(p, 18, 8, 18, 11)
    p.drawArc(QRectF(6, 12, 10, 8), 180 * 16, 180 * 16)
    _line(p, 6, 13, 6, 16)
    _line(p, 10, 12, 14, 12)


def _code(p: QPainter) -> None:
    _line(p, 9, 7, 4, 12)
    _line(p, 4, 12, 9, 17)
    _line(p, 15, 7, 20, 12)
    _line(p, 20, 12, 15, 17)


def _git(p: QPainter) -> None:
    _line(p, 7, 5, 7, 19)
    _dot(p, 7, 5, 1.5)
    _dot(p, 7, 12, 1.5)
    _dot(p, 16, 8, 1.5)
    _line(p, 7, 12, 16, 12)
    _line(p, 16, 12, 16, 8)


def _layers(p: QPainter) -> None:
    p.drawPolygon([QPointF(12, 4), QPointF(21, 8), QPointF(12, 12), QPointF(3, 8)])
    _line(p, 3, 12, 12, 16)
    _line(p, 21, 12, 12, 16)
    _line(p, 3, 16, 12, 20)
    _line(p, 21, 16, 12, 20)


def _eye(p: QPainter) -> None:
    p.drawArc(QRectF(3, 6, 18, 12), 20 * 16, 140 * 16)
    p.drawArc(QRectF(3, 6, 18, 12), 200 * 16, 140 * 16)
    _oval(p, 9, 9, 6, 6)


def _play(p: QPainter) -> None:
    p.drawPolygon([QPointF(8, 5), QPointF(18, 12), QPointF(8, 19)])


def _pause(p: QPainter) -> None:
    _box(p, 7, 5, 3.2, 14, 1)
    _box(p, 13.8, 5, 3.2, 14, 1)


def _stop(p: QPainter) -> None:
    _box(p, 6, 6, 12, 12, 2)


def _flame(p: QPainter) -> None:
    p.drawArc(QRectF(7, 8, 10, 12), 200 * 16, 220 * 16)
    _line(p, 12, 3, 10, 10)
    _line(p, 10, 10, 14, 8)
    _line(p, 14, 8, 15, 14)


def _leaf(p: QPainter) -> None:
    p.drawArc(QRectF(4, 4, 16, 16), 40 * 16, 200 * 16)
    _line(p, 7, 17, 16, 8)


def _map(p: QPainter) -> None:
    p.drawPolygon(
        [
            QPointF(4, 6),
            QPointF(9, 4),
            QPointF(15, 7),
            QPointF(20, 5),
            QPointF(20, 18),
            QPointF(15, 20),
            QPointF(9, 17),
            QPointF(4, 19),
        ]
    )
    _line(p, 9, 4, 9, 17)
    _line(p, 15, 7, 15, 20)


def _compass(p: QPainter) -> None:
    _oval(p, 3, 3, 18, 18)
    p.drawPolygon([QPointF(12, 7), QPointF(14, 14), QPointF(12, 12), QPointF(10, 14)])
    _line(p, 12, 12, 16, 16)


def _anchor(p: QPainter) -> None:
    _oval(p, 9, 3, 6, 6)
    _line(p, 12, 9, 12, 20)
    _line(p, 6, 14, 18, 14)
    p.drawArc(QRectF(5, 12, 14, 10), 180 * 16, 180 * 16)


def _phone(p: QPainter) -> None:
    _box(p, 7, 2, 10, 20, 2)
    _line(p, 10, 18, 14, 18)


def _camera(p: QPainter) -> None:
    _box(p, 3, 7, 18, 12, 2)
    _line(p, 9, 7, 10, 5)
    _line(p, 10, 5, 14, 5)
    _line(p, 14, 5, 15, 7)
    _oval(p, 9, 10, 6, 6)


def _bookmark(p: QPainter) -> None:
    p.drawPolygon(
        [
            QPointF(6, 3),
            QPointF(18, 3),
            QPointF(18, 21),
            QPointF(12, 16),
            QPointF(6, 21),
        ]
    )


def _tag(p: QPainter) -> None:
    p.drawPolygon(
        [
            QPointF(3, 12),
            QPointF(12, 3),
            QPointF(21, 3),
            QPointF(21, 12),
            QPointF(12, 21),
        ]
    )
    _dot(p, 16, 8, 1.1)


def _hash(p: QPainter) -> None:
    _line(p, 9, 4, 7, 20)
    _line(p, 17, 4, 15, 20)
    _line(p, 4, 9, 20, 9)
    _line(p, 3, 15, 19, 15)


def _activity(p: QPainter) -> None:
    _line(p, 2, 12, 7, 12)
    _line(p, 7, 12, 10, 5)
    _line(p, 10, 5, 14, 19)
    _line(p, 14, 19, 17, 12)
    _line(p, 17, 12, 22, 12)


def _truck(p: QPainter) -> None:
    _box(p, 2, 7, 12, 8, 1)
    _line(p, 14, 10, 18, 10)
    _line(p, 18, 10, 21, 13)
    _line(p, 21, 13, 21, 15)
    _line(p, 14, 15, 21, 15)
    _oval(p, 5, 15, 4, 4)
    _oval(p, 15, 15, 4, 4)


def _flag(p: QPainter) -> None:
    _line(p, 6, 3, 6, 21)
    p.drawPolygon([QPointF(6, 4), QPointF(18, 7), QPointF(6, 11)])


def _refresh(p: QPainter) -> None:
    p.drawArc(QRectF(5, 5, 14, 14), 40 * 16, 280 * 16)
    _line(p, 16, 5, 19, 4)
    _line(p, 16, 5, 16, 8)


def _power(p: QPainter) -> None:
    _line(p, 12, 3, 12, 12)
    p.drawArc(QRectF(5, 6, 14, 14), -50 * 16, 280 * 16)


def _message(p: QPainter) -> None:
    _box(p, 3, 4, 18, 12, 2)
    p.drawPolygon([QPointF(8, 16), QPointF(8, 20), QPointF(13, 16)])


def _image(p: QPainter) -> None:
    _box(p, 3, 4, 18, 16, 2)
    _line(p, 4, 16, 9, 11)
    _line(p, 9, 11, 13, 15)
    _line(p, 13, 15, 16, 12)
    _line(p, 16, 12, 20, 16)
    _dot(p, 8, 8, 1.1)


def _table(p: QPainter) -> None:
    _box(p, 3, 4, 18, 16, 1.5)
    _line(p, 3, 9, 21, 9)
    _line(p, 3, 14, 21, 14)
    _line(p, 10, 4, 10, 20)


def _list(p: QPainter) -> None:
    for y in (6, 12, 18):
        _dot(p, 5, y, 1)
        _line(p, 9, y, 19, y)


def _grid(p: QPainter) -> None:
    for x in (4, 10, 16):
        for y in (4, 10, 16):
            _box(p, x, y, 4, 4, 1)


def _sliders(p: QPainter) -> None:
    _line(p, 5, 5, 5, 19)
    _line(p, 12, 5, 12, 19)
    _line(p, 19, 5, 19, 19)
    _oval(p, 3, 8, 4, 4)
    _oval(p, 10, 13, 4, 4)
    _oval(p, 17, 7, 4, 4)


def _share(p: QPainter) -> None:
    _dot(p, 6, 12, 2)
    _dot(p, 17, 6, 2)
    _dot(p, 17, 18, 2)
    _line(p, 8, 11, 15, 7)
    _line(p, 8, 13, 15, 17)


def _copy(p: QPainter) -> None:
    _box(p, 7, 7, 12, 13, 2)
    _line(p, 5, 16, 5, 5)
    _line(p, 5, 5, 15, 5)


def _trash(p: QPainter) -> None:
    _line(p, 5, 7, 19, 7)
    _line(p, 9, 4, 15, 4)
    _box(p, 6, 7, 12, 13, 1.5)
    _line(p, 10, 10, 10, 17)
    _line(p, 14, 10, 14, 17)


def _edit(p: QPainter) -> None:
    _line(p, 4, 20, 8, 19)
    _line(p, 8, 19, 19, 8)
    _line(p, 19, 8, 16, 5)
    _line(p, 16, 5, 5, 16)
    _line(p, 5, 16, 4, 20)


def _plus(p: QPainter) -> None:
    _line(p, 12, 5, 12, 19)
    _line(p, 5, 12, 19, 12)


def _minus(p: QPainter) -> None:
    _line(p, 5, 12, 19, 12)


def _info(p: QPainter) -> None:
    _oval(p, 3, 3, 18, 18)
    _line(p, 12, 11, 12, 17)
    _dot(p, 12, 8, 1)


ICONS: dict[str, tuple[str, object]] = {
    "server": ("servidor computador maquina rack", _server),
    "monitor": ("tela monitor desktop", _monitor),
    "laptop": ("notebook laptop", _laptop),
    "terminal": ("terminal console ssh comando", _terminal),
    "cloud": ("nuvem cloud", _cloud),
    "database": ("banco dados database tabela", _database),
    "lock": ("cadeado seguro trava", _lock),
    "key": ("chave senha acesso", _key),
    "shield": ("escudo protecao seguranca", _shield),
    "globe": ("internet web mundo site", _globe),
    "network": ("rede nos conexao", _network),
    "folder": ("pasta diretorio arquivos", _folder),
    "file": ("arquivo documento", _file),
    "box": ("pacote caixa container docker", _package),
    "rocket": ("foguete deploy lancar", _rocket),
    "wrench": ("ferramenta chave inglesa", _wrench),
    "gear": ("engrenagem config configuracao", _gear),
    "user": ("usuario pessoa", _user),
    "users": ("equipe grupo usuarios", _users),
    "bug": ("bug erro inseto", _bug),
    "bolt": ("raio energia rapido", _bolt),
    "wifi": ("wifi sinal wireless", _wifi),
    "plug": ("tomada cabo energia", _plug),
    "cpu": ("processador chip cpu", _cpu),
    "disk": ("disco hd armazenamento", _disk),
    "mail": ("email carta mensagem", _mail),
    "bell": ("sino alerta notificacao", _bell),
    "search": ("busca lupa pesquisar", _search),
    "chart": ("grafico metricas", _chart),
    "home": ("casa inicio home", _home),
    "building": ("predio empresa escritorio", _building),
    "star": ("estrela favorito", _star),
    "heart": ("coracao", _heart),
    "check": ("certo ok sucesso", _check),
    "alert": ("aviso atencao alerta", _alert),
    "clock": ("relogio tempo", _clock),
    "calendar": ("calendario data", _calendar),
    "download": ("baixar download", _download),
    "upload": ("enviar upload", _upload),
    "link": ("link elo url", _link),
    "code": ("codigo programacao", _code),
    "git": ("git branch versao", _git),
    "layers": ("camadas layers", _layers),
    "eye": ("olho ver observar", _eye),
    "play": ("executar play iniciar", _play),
    "pause": ("pausar", _pause),
    "stop": ("parar stop", _stop),
    "flame": ("fogo calor", _flame),
    "leaf": ("folha planta", _leaf),
    "map": ("mapa", _map),
    "compass": ("bussola navegacao", _compass),
    "anchor": ("ancora porto", _anchor),
    "phone": ("telefone celular", _phone),
    "camera": ("camera foto", _camera),
    "bookmark": ("marcador bookmark", _bookmark),
    "tag": ("etiqueta tag", _tag),
    "hash": ("cerquilha hash", _hash),
    "activity": ("pulso atividade metricas", _activity),
    "truck": ("caminhao entrega", _truck),
    "flag": ("bandeira", _flag),
    "refresh": ("atualizar recarregar", _refresh),
    "power": ("ligar energia", _power),
    "message": ("chat conversa mensagem", _message),
    "image": ("imagem foto", _image),
    "table": ("tabela grade", _table),
    "list": ("lista", _list),
    "grid": ("grade icones", _grid),
    "sliders": ("ajustes controles", _sliders),
    "share": ("compartilhar", _share),
    "copy": ("copiar duplicar", _copy),
    "trash": ("lixeira excluir apagar", _trash),
    "edit": ("editar lapis", _edit),
    "plus": ("mais adicionar", _plus),
    "minus": ("menos remover", _minus),
    "info": ("informacao info", _info),
}


def resolve_icon(icon_id: str) -> str:
    if icon_id in ICONS:
        return icon_id
    return DEFAULT_ICON


def icon_words(icon_id: str) -> str:
    words, _draw = ICONS[resolve_icon(icon_id)]
    return words


def icon_pixmap(icon_id: str, size: int) -> QPixmap:
    _words, draw = ICONS[resolve_icon(icon_id)]
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    scale = size / _VIEW
    painter.scale(scale, scale)
    _pen(painter)
    draw(painter)
    painter.end()
    return pixmap


def icon_picture(icon_id: str, size: int) -> QIcon:
    return QIcon(icon_pixmap(icon_id, size))


def catalog() -> list[tuple[str, str]]:
    return [(icon_id, words) for icon_id, (words, _draw) in ICONS.items()]

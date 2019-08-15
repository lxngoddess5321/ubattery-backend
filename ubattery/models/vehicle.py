import sqlalchemy.dialects.mysql as mysql_type

from ubattery.extensions import mysql


class Vehicle(mysql.Model):
    """vehicle_id: 4F37195C1A908CFBE0532932A8C0EECB"""

    __tablename__ = 'yutong_vehicle1'

    id = mysql.Column(mysql_type.INTEGER, primary_key=True)

    province = mysql.Column(mysql_type.VARCHAR(100), comment='省')

    city = mysql.Column(mysql_type.VARCHAR(100), comment='城市')

    timestamp = mysql.Column(mysql_type.DATETIME, index=True, comment='CST 时间')

    bty_t_vol = mysql.Column(mysql_type.DECIMAL(10, 2), comment='电池总电压')

    bty_t_curr = mysql.Column(mysql_type.DECIMAL(10, 2), comment='电池总电流')

    battery_soc = mysql.Column(mysql_type.DECIMAL(5, 2), comment='SOC')

    s_b_max_t = mysql.Column(mysql_type.INTEGER, comment='电池最高温度')

    max_t_s_b_num = mysql.Column(mysql_type.INTEGER, comment='最高温度电池号')

    s_b_min_t = mysql.Column(mysql_type.INTEGER, comment='电池最低温度')

    min_t_s_b_num = mysql.Column(mysql_type.INTEGER, comment='最低温度电池号')

    s_b_max_v = mysql.Column(mysql_type.DECIMAL(10, 6), comment='电池最高电压')

    max_v_e_core_num = mysql.Column(mysql_type.INTEGER, comment='最高电压电芯号')

    s_b_min_v = mysql.Column(mysql_type.DECIMAL(10, 6), comment='电池最低电压')

    min_v_e_core_num = mysql.Column(mysql_type.INTEGER, comment='最低电压电芯号')

    p_t_p = mysql.Column(mysql_type.DECIMAL(10, 2), comment='正向累计电量')

    r_t_p = mysql.Column(mysql_type.DECIMAL(10, 2), comment='反向累计电量')

    total_mileage = mysql.Column(mysql_type.INTEGER, comment='总里程')

    bty_sys_rated_capacity = mysql.Column(mysql_type.INTEGER, comment='额定容量')

    bty_sys_rated_consumption = mysql.Column(mysql_type.INTEGER, comment='额定能量')

    met_spd = mysql.Column(mysql_type.INTEGER, comment='车速')

    byt_ma_sys_state = mysql.Column(mysql_type.INTEGER, comment='充电状态，6 代表充电中')
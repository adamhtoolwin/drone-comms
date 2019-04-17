namespace cpp base
namespace d base
namespace dart base
namespace java base
namespace php base
namespace perl base
namespace haxe base
namespace netcore base

struct Coordinate {
    1: double latitude,
    2: double longitude,
}

service Drone{
    void takeoff(1:double altitude),
    
    void land(),

    void fly_to(1:double latitude, 2:double longitude, 3:double altitude),

    void clear_missions(),

    void download_missions(),

    void change_mode(1:string mode),

    bool report_status(1:i32 drone_id),

    void add_delivery_mission(1:double latitude, 2:double longitude, 3:double altitude),

    void arm(),

    void disarm(),

    void add_farm_mission(1:list<Coordinate> coordinates),
}

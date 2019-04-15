namespace cpp base
namespace d base
namespace dart base
namespace java base
namespace php base
namespace perl base
namespace haxe base
namespace netcore base

service Drone{
    void takeoff(1:double altitude),
    
    void land(),

    void fly_to(1:double latitude, 2:double longitude, 3:double altitude)

    void clear_missions(),

    void download_missions(),

    void change_mode(1:string mode)

    void report_status(1:string drone_id)

    void add_delivery_mission(1:double latitude, 2:double longitude, 3:double altitude)
}

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
}
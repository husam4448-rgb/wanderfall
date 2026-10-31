package com.survivalparadise.nativegame;

/** V78 confirms follower travel and dynamic light cache invalidation at stop. */
public final class V78FlashlightTest {
    static void ok(boolean pass,String msg){if(!pass)throw new AssertionError(msg);}
    static long lights(float beamX,float beamAngle,float pointX){
        long hash=LightCacheV78.seed(1,1);
        hash=LightCacheV78.point(hash,pointX,42f,65f,0xfffee6ba);
        return LightCacheV78.beam(hash,beamX,108f,beamAngle,0f,490f);
    }
    public static void main(String[]args){
        long still=lights(100f,1f,200f);
        ok(still==lights(100f,1f,200f),"stationary geometry changed");
        ok(still!=lights(100.7f,1f,200f),"moving flashlight incorrectly cached");
        ok(still!=lights(100f,-1f,200f),"torch turn incorrectly cached");
        ok(still!=lights(100f,1f,201f),"moving projectile incorrectly cached");
        ok(still!=LightCacheV78.seed(0,1),"source count incorrectly cached");
        ok(LightCacheV78.canReuse(true,true,true,true,true,still,still),
           "stationary camera should reuse unchanged lights");
        ok(!LightCacheV78.canReuse(true,true,true,true,true,still,lights(101f,1f,200f)),
           "stationary camera must redraw following flashlight");
        ok(!LightCacheV78.canReuse(true,true,false,true,true,still,still),
           "moving camera must redraw");
        ok(!LightCacheV78.canReuse(false,true,true,true,true,still,still),
           "disabled cache may not reuse");
        for(int fps:new int[]{30,60,90,120}){
            float distance=500f;int frames=0;
            boolean everMoved=false;
            while(distance>FollowerArrivalV78.STOP_RADIUS+.001f&&frames<2400){
                float step=FollowerArrivalV78.step(distance,1f/fps,198f);
                ok(step>=0f&&step<=distance-FollowerArrivalV78.STOP_RADIUS+.00001f,
                   "follower overshoots at "+fps+" fps");
                distance-=step;frames++;everMoved|=step>0f;
            }
            ok(everMoved&&distance>=FollowerArrivalV78.STOP_RADIUS-.01f&&
              distance<=FollowerArrivalV78.STOP_RADIUS+.15f,
              "stationary target settle "+fps+" fps");
            ok(FollowerArrivalV78.step(distance,1f/fps,198f)<.05f,
              "arrival jitter "+fps);
        }
        ok(!FollowerArrivalV78.shouldTurn(10f,26f),"arrival turns back");
        ok(FollowerArrivalV78.shouldTurn(-120f,160f),"distant follower can turn");
        ok(!FollowerArrivalV78.visuallyWalking(.08f),"microsteps toggle sprites");
        ok(FollowerArrivalV78.visuallyWalking(2f),"real travel animates");
        System.out.println("V78 PASS: mobile beams and point lights invalidate cache; stable arrival 30–120 FPS");
    }
}

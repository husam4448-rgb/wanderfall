package com.survivalparadise.nativegame;

/** Pure-Java regression tests against the native game animation state machine. */
public final class AnimationCycleTest {
    static void check(boolean ok,String label) {
        if(!ok) throw new AssertionError(label);
    }
    public static void main(String[] args) {
        AnimationCycle player=new AnimationCycle();
        AnimationCycle companion=new AnimationCycle();
        AnimationCycle bandit=new AnimationCycle();
        AnimationCycle[] actors={player,companion,bandit};
        for(int i=0;i<actors.length;i++) {
            AnimationCycle a=actors[i];
            check(a.frame()==0 && !a.isWalking(),"new actor is neutral idle");
            a.step(true,.016f,7f);
            check(a.frame()==0 && a.isWalking(),"walk starts on first approved pose");
            a.step(true,.19f,7f);
            check(a.frame()>0,"actor reaches a visible walking frame");
            a.step(false,.016f,7f);
            check(a.frame()==0&&!a.isWalking(),"STOP immediately selects neutral frame");
            for(int n=0;n<30;n++){
                a.step(false,.016f,7f);
                check(a.frame()==0,"idle never cycles into the walk sequence");
            }
            a.step(true,.016f,7f);
            check(a.frame()==0,"walking resumes at first pose, not stale mid-stride");
            a.step(true,.27f,7f);
            check(a.frame()>0,"walking advances after restart");
            a.reset();
            check(a.frame()==0,"release/focus loss restores idle");
            for(int n=0;n<20000;n++)a.step(true,.016f,7f);
            check(a.frame()>=0 && a.frame()<4,"long session keeps valid frames");
            a.step(false,.016f,7f);
            check(a.frame()==0,"long-session stop restores neutral pose");
        }
        // Moving joystick against an impassable wall passes 'actuallyMoving=false':
        player.step(true,.3f,7f);
        player.step(true,.3f,7f);
        player.step(false,.016f,7f);
        check(player.frame()==0,"blocked movement does not animate walking");
        // Firing/aiming do not change the locomotion cycle.
        for(int i=0;i<300;i++) {
            player.step(false,.016f,7f);
            check(player.frame()==0,"stationary aiming/firing stays idle");
        }
        System.out.println("V37 IDLE/WALK STATE TESTS PASS: player, companions and enemies");
    }
}

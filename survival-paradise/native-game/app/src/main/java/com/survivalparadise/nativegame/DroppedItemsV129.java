package com.survivalparadise.nativegame;
import java.util.ArrayList;
import java.util.Iterator;

/**
 * Persistent player-discarded stacks, tracked in paused in-game solar time.
 * Unlike transient pickup sparks, these stacks remain for a user-selected
 * one or two in-game days and survive reload/region travel.
 */
public final class DroppedItemsV129 {
    public static final int TYPES=39, MAX=256;
    public static final float USE_RADIUS=110f;
    public static final class Stack {
        public final long id;public final int type,quantity;public final float x,y;
        public final String scene;public final float expiresAt;
        private Stack(long id,int t,int n,float x,float y,String scene,float expiry){
            this.id=id;type=t;quantity=n;this.x=x;this.y=y;this.scene=scene;expiresAt=expiry;
        }
    }
    public final ArrayList<Stack> stacks=new ArrayList<>();
    private long next=1;
    public void clear(){stacks.clear();next=1;}
    public static float time(int day,float minute){
        return Math.max(1,day)*1440f+Math.max(0f,Math.min(1440f,minute));
    }
    public static int days(int setting){return Math.max(1,Math.min(2,setting));}
    public Stack drop(int type,int quantity,float x,float y,String scene,float now,int days){
        if(type<0||type>=TYPES||quantity<=0||quantity>9999||
           !Float.isFinite(x)||!Float.isFinite(y)||!Float.isFinite(now)||
           scene==null||scene.isEmpty()||scene.contains(",")||scene.contains(";")||
           stacks.size()>=MAX)return null;
        Stack s=new Stack(next++,type,quantity,x,y,scene,
                          now+days(days)*1440f);
        stacks.add(s);return s;
    }
    public boolean take(Stack s){return s!=null&&stacks.remove(s);}
    public boolean contains(Stack s){return s!=null&&stacks.contains(s);}
    public Stack nearest(float x,float y,String scene,float radius){
        float best=radius*radius;Stack found=null;
        for(Stack s:stacks){
            if(!s.scene.equals(scene))continue;
            float dx=s.x-x,dy=s.y-y,d=dx*dx+dy*dy;
            if(d<=best){best=d;found=s;}
        }
        return found;
    }
    public void expire(float now){
        for(Iterator<Stack> it=stacks.iterator();it.hasNext();){
            if(it.next().expiresAt<=now)it.remove();
        }
    }
    public String encode(){
        StringBuilder out=new StringBuilder();
        for(Stack s:stacks){
            if(out.length()>0)out.append(';');
            out.append(s.id).append(',').append(s.type).append(',')
               .append(s.quantity).append(',').append(s.x).append(',')
               .append(s.y).append(',').append(s.expiresAt).append(',')
               .append(s.scene);
        }
        return out.toString();
    }
    public void decode(String data){
        clear();if(data==null||data.isEmpty())return;
        for(String row:data.split(";")){
            if(stacks.size()>=MAX)break;
            String[] p=row.split(",",-1);if(p.length!=7)continue;
            try{
                long id=Long.parseLong(p[0]);int t=Integer.parseInt(p[1]);
                int n=Integer.parseInt(p[2]);
                float x=Float.parseFloat(p[3]),y=Float.parseFloat(p[4]);
                float expiry=Float.parseFloat(p[5]);String scene=p[6];
                if(id<1||t<0||t>=TYPES||n<=0||n>9999||
                   !Float.isFinite(x)||!Float.isFinite(y)||
                   !Float.isFinite(expiry)||Math.abs(x)>2_000_000f||
                   Math.abs(y)>2_000_000f||scene.isEmpty()||
                   scene.length()>110)continue;
                boolean collision=false;for(Stack old:stacks)
                    if(old.id==id){collision=true;break;}
                if(collision)continue;
                stacks.add(new Stack(id,t,n,x,y,scene,expiry));
                next=Math.max(next,id+1);
            }catch(NumberFormatException ignored){}
        }
    }
}

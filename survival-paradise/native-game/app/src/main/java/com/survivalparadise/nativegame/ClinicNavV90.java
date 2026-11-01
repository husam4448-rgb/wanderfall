package com.survivalparadise.nativegame;
/** Precomputed low-resolution room navmesh: no outdoor tiles or frame-time allocations. */
public final class ClinicNavV90 {
    public static final int CELL=51;
    public final int w,h;
    final boolean[] free;
    final int[] queue,prev;
    public ClinicNavV90(ClinicInteriorV89 map){
        w=(ClinicInteriorV89.WIDTH+CELL-1)/CELL;
        h=(ClinicInteriorV89.HEIGHT+CELL-1)/CELL;
        free=new boolean[w*h];queue=new int[w*h];prev=new int[w*h];
        for(int y=0;y<h;y++)for(int x=0;x<w;x++)
            free[y*w+x]=!map.blocked(x*CELL+CELL*.5f,
                y*CELL+CELL*.5f,10);
    }
    public float[] next(float px,float py,float tx,float ty){
        int sx=Math.max(0,Math.min(w-1,(int)(px/CELL)));
        int sy=Math.max(0,Math.min(h-1,(int)(py/CELL)));
        int gx=Math.max(0,Math.min(w-1,(int)(tx/CELL)));
        int gy=Math.max(0,Math.min(h-1,(int)(ty/CELL)));
        int start=sy*w+sx,goal=gy*w+gx;
        if(start==goal)return new float[]{tx,ty};
        if(!free[start]||!free[goal])return new float[]{tx,ty};
        java.util.Arrays.fill(prev,-1);
        queue[0]=start;prev[start]=start;int read=0,write=1;
        final int[] dx={1,-1,0,0},dy={0,0,1,-1};
        while(read<write){
            int current=queue[read++];if(current==goal)break;
            int x=current%w,y=current/w;
            for(int i=0;i<4;i++){
                int nx=x+dx[i],ny=y+dy[i];
                if(nx<0||ny<0||nx>=w||ny>=h)continue;
                int id=ny*w+nx;
                if(free[id]&&prev[id]==-1){
                    prev[id]=current;queue[write++]=id;
                }
            }
        }
        if(prev[goal]<0)return new float[]{tx,ty};
        int step=goal;
        while(prev[step]!=start&&step!=start)step=prev[step];
        return new float[]{(step%w+.5f)*CELL,(step/w+.5f)*CELL};
    }
}

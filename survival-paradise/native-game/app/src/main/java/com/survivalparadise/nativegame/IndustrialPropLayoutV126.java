package com.survivalparadise.nativegame;

/**
 * One scene-geometry source for V126 exterior art AND physical collisions.
 * Values are authored in world units, calibrated against the approved
 * 200-character in-game height, without altering any original art pixels.
 */
public final class IndustrialPropLayoutV126 {
    private IndustrialPropLayoutV126(){}
    // Source-order sprite indices from the original 24-artwork pack.
    static final int SCRAP=0, CONVEYOR=5, REINFORCED=6,
        TRANSFORMER=8, FORKLIFT=9, TRUCK=10, VERTICAL=11,
        BELT=12, TANKS=13, PIPE=18, SILOS=20;

    public static final class Prop {
        public final int sprite;
        public final float x,y,w,h;
        public final boolean solid;
        public final float left,top,right,bottom;
        private Prop(int sprite,float x,float y,float w,float h,
                     boolean solid,float left,float top,float right,float bottom){
            this.sprite=sprite;this.x=x;this.y=y;this.w=w;this.h=h;
            this.solid=solid;this.left=left;this.top=top;
            this.right=right;this.bottom=bottom;
        }
        /** Match the visible approved PNG content, not its transparent margin. */
        public boolean blocks(float worldX,float worldY,float radius,
                              IndustrialOpenWorldV124.Plot lot){
            if(!solid)return false;
            float l=lot.x+x+w*left,t=lot.y+y+h*top;
            float r=lot.x+x+w*right,b=lot.y+y+h*bottom;
            float dx=Math.max(l-worldX,Math.max(0f,worldX-r));
            float dy=Math.max(t-worldY,Math.max(0f,worldY-b));
            return dx*dx+dy*dy<=radius*radius;
        }
    }

    private static Prop art(int id,float x,float y,float w,float h,boolean solid){
        // Values measured from source PNG alpha (>155). These are conservative
        // visual-content bounds, not fabricated full-sprite rectangles.
        float left=0.02f,top=0.10f,right=0.98f,bottom=0.90f;
        switch(id){
            case TRANSFORMER: left=.037f;top=.045f;right=.962f;bottom=.949f;break;
            case FORKLIFT: left=.033f;top=.122f;right=.974f;bottom=.880f;break;
            case TRUCK: left=.022f;top=.233f;right=.977f;bottom=.789f;break;
            case BELT: left=.008f;top=.191f;right=.991f;bottom=.815f;break;
            case TANKS: left=.038f;top=.099f;right=.963f;bottom=.854f;break;
            case PIPE: left=.018f;top=.187f;right=.991f;bottom=.805f;break;
            case SCRAP: left=.022f;top=.128f;right=.994f;bottom=.918f;break;
            case CONVEYOR: left=.017f;top=.129f;right=.984f;bottom=.817f;break;
            case VERTICAL: left=.298f;top=.006f;right=.701f;bottom=.989f;break;
            case REINFORCED: left=.018f;top=.155f;right=.982f;bottom=.843f;break;
            case SILOS: left=.060f;top=.088f;right=.948f;bottom=.886f;break;
            default:break;
        }
        return new Prop(id,x,y,w,h,solid,left,top,right,bottom);
    }

    // World props are sized relative to the player, not as small icons.
    // Fenced yard openings and factory entrance driveways stay unobstructed.
    private static final Prop[] FACTORY_EVEN={
        art(TANKS,1010,355,215,218,true),
        art(TRANSFORMER,1002,840,205,181,true),
        art(BELT,177,891,258,188,true),
        art(PIPE,1015,693,177,148,true),
        art(FORKLIFT,871,1004,270,192,true)
    };
    private static final Prop[] FACTORY_FOUNDRY={
        art(SILOS,1010,355,215,218,true),
        art(TRANSFORMER,1002,840,205,181,true),
        art(BELT,177,891,258,188,true),
        art(PIPE,1015,693,177,148,true),
        art(FORKLIFT,871,1004,270,192,true)
    };
    private static final Prop[] FACTORY_ODD={
        art(TANKS,1010,355,215,218,true),
        art(TRANSFORMER,1002,840,205,181,true),
        art(BELT,177,891,258,188,true),
        art(PIPE,1015,693,177,148,true),
        art(TRUCK,906,1004,298,198,true)
    };
    private static final Prop[] STORAGE_YARD={
        art(SCRAP,218,694,252,188,true),
        art(CONVEYOR,884,766,296,205,true),
        art(VERTICAL,205,907,248,209,true),
        art(REINFORCED,880,969,248,189,true),
        art(TRUCK,954,543,271,194,true)
    };

    public static Prop[] forPlot(IndustrialOpenWorldV124.Plot lot){
        if(!lot.developed())return new Prop[0];
        if(lot.type==IndustrialOpenWorldV124.YARD)return STORAGE_YARD;
        if(lot.kind==2)return FACTORY_FOUNDRY;
        return (lot.kind&1)==0?FACTORY_EVEN:FACTORY_ODD;
    }
    public static boolean blocks(IndustrialOpenWorldV124.Plot lot,float x,float y,float radius){
        for(Prop p:forPlot(lot))if(p.blocks(x,y,radius,lot))return true;
        return false;
    }
}

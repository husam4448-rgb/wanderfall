package com.survivalparadise.nativegame;

/**
 * Visual-only indoor character visibility. Uses the same aiming cone and
 * wall-occlusion rules as the existing environment vision mask.
 * Does not modify AI, collision, dialogue or actor save state.
 */
public final class IndoorCharacterVisionV127 {
    private IndoorCharacterVisionV127(){}

    /**
     * Draw a character only if some meaningful part of the head/torso/body is
     * actually visible. The drawing is ALSO clipped to the traced cone polygon
     * so limbs, weapons and labels cannot spill into the hidden portion.
     */
    public static boolean visible(ClinicVisionV90 cone, ClinicInteriorV89 world,
            float eyeX,float eyeY,float aimX,float aimY,float actorX,float actorFeetY){
        float dx=actorX-eyeX;
        float centerY=actorFeetY-65f;
        float dy=centerY-eyeY;
        if(dx*dx+dy*dy>(ClinicVisionV90.RANGE+55f)*(ClinicVisionV90.RANGE+55f))
            return false;
        return cone.visible(eyeX,eyeY,aimX,aimY,actorX,centerY,world)
            || cone.visible(eyeX,eyeY,aimX,aimY,actorX,actorFeetY-99f,world)
            || cone.visible(eyeX,eyeY,aimX,aimY,actorX,actorFeetY-24f,world);
    }
}

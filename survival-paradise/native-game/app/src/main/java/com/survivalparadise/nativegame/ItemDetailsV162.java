package com.survivalparadise.nativegame;

import java.util.Locale;

/** Inspectable stats are sourced from exactly the live gameplay formulas. */
public final class ItemDetailsV162 {
    private ItemDetailsV162(){}
    public static String describe(GameView game,int type,int quantity){
        StringBuilder sb=new StringBuilder();
        if(GearStatsV162.isWearable(type)){
            int socket=game.inventorySlotV141(type);
            sb.append(socket==0?"HEAD EQUIPMENT":
                socket==2?"TORSO ARMOR":socket==3?"LEG EQUIPMENT":"FOOTWEAR");
            sb.append("\nARMOR: +").append(GearStatsV162.armor(type))
                .append("% incoming damage reduction");
            int agi=GearStatsV162.agility(type);
            sb.append("\nAGILITY: ").append(agi>=0?"+":"")
                .append(agi).append("% movement speed");
            float regen=GearStatsV162.healthRegen(type);
            sb.append("\nHEALTH REGEN: ").append(regen>0f?
                String.format(Locale.US,"+%.3f HP/sec",regen):"none");
            sb.append("\nEQUIPPED: ")
                .append(game.equippedGearTypeV162(socket)==type?"YES":"NO");
            if(socket==0)sb.append("\nHEAD VISUALS: disabled");
        }else if(type>=24&&type<=26){
            int extra=FieldFindsV91.CAPACITY_BONUS[type-24];
            float load=game.inventoryLoadV162();
            float old=GearStatsV162.encumbrance(load,0);
            float next=GearStatsV162.encumbrance(load,extra);
            sb.append("BACKPACK • CARRY CAPACITY")
                .append("\nCAPACITY: 40 + ").append(extra).append(" = ")
                .append(40+extra).append(" load units")
                .append("\nENCUMBRANCE: ").append(Math.round(old))
                .append("% → ").append(Math.round(next)).append("%")
                .append("\nENCUMBRANCE REDUCTION: ")
                .append(Math.round(GearStatsV162.backpackReductionPercent(load,extra)))
                .append("% at current load")
                .append("\nEQUIPPED: ")
                .append(game.fieldFindsV91.equipped==type-24?"YES":"NO");
        }else if(OutfitInventoryV140.slot(type)==3){
            int gun=OutfitInventoryV140.style(type);
            if(gun==3){
                sb.append("UTILITY • FLASHLIGHT\nAMMO: none")
                    .append("\nEFFECT: directional illumination");
            }else if(gun==11){
                sb.append("MELEE • RED AXE")
                    .append("\nDAMAGE: ").append(GameView.POWER[gun])
                    .append(" per hit\nMAGAZINE: none")
                    .append("\nSWING INTERVAL: ")
                    .append(String.format(Locale.US,"%.2f sec",GameView.RATES[gun]));
            }else{
                sb.append("FIREARM • ")
                    .append(OutfitInventoryV140.WEAPON_NAMES[gun].toUpperCase(Locale.US));
                if(gun==7)sb.append("\nDAMAGE: 5 pellets × ")
                    .append(GameView.POWER[gun]/2).append(" each");
                else sb.append("\nDAMAGE: ").append(GameView.POWER[gun])
                    .append(" / projectile");
                sb.append("\nRATE OF FIRE: ")
                    .append(String.format(Locale.US,"%.2f shots/sec",
                        1f/GameView.RATES[gun]));
                sb.append("\nMAGAZINE: ").append(GameView.MAG[gun]);
                int ammo=AmmoInventoryV143.forGun(gun);
                sb.append("\nAMMO TYPE: ")
                    .append(ammo<0?"NONE":AmmoInventoryV143.name(ammo));
                sb.append("\nRELOAD TIME: ")
                    .append(String.format(Locale.US,"%.2f sec",ReloadProfileV151.duration(gun)));
                sb.append("\nBULLET SPEED: ")
                    .append(Math.round(Ballistics.SPEED[gun]))
                    .append(" world units/sec");
            }
            sb.append("\nEQUIPPED: ").append(game.gun==gun?"YES":"NO");
        }else if(AmmoInventoryV143.valid(type)){
            sb.append("AMMUNITION • ").append(AmmoInventoryV143.name(type))
                .append("\nCOMPATIBLE WEAPONS: ");
            boolean first=true;
            for(int gun=0;gun<OutfitInventoryV140.WEAPON_NAMES.length;gun++){
                if(AmmoInventoryV143.forGun(gun)!=type)continue;
                if(!first)sb.append(", ");
                sb.append(OutfitInventoryV140.WEAPON_NAMES[gun]);
                first=false;
            }
            sb.append("\nUSE: reload compatible magazines");
        }else if(type==OutfitInventoryV140.ROUNDS){
            sb.append("GENERIC LOOSE AMMUNITION")
                .append("\nUSE: reserve if specific-caliber ammo is exhausted");
        }else if(type==1){
            sb.append("MEDKIT • CONSUMABLE\nHEALS: +40 HP")
                .append("\nMAXIMUM HEALTH: 100 HP");
        }else if(type==12){
            sb.append("BANDAGE • CONSUMABLE\nHEALS: +24 HP")
                .append("\nMAXIMUM HEALTH: 100 HP");
        }else if(type==13){
            sb.append("ENERGY RATION • CONSUMABLE")
                .append("\nRESTORES: +50 stamina")
                .append("\nREDUCES: −20 fatigue");
        }else if(type==3){
            sb.append("FOOD • CONSUMABLE\nRESTORES: +30 hunger");
        }else if(type==4){
            sb.append("WATER • CONSUMABLE\nRESTORES: +35 thirst");
        }else if(type==2){
            sb.append("AMMO PACK • CONSUMABLE")
                .append("\nEFFECT: fills current magazine when normal reserve is unavailable");
        }else if(type>=8&&type<=11){
            sb.append("CRAFTED STRUCTURE")
                .append("\nEFFECT: place in a valid world location");
        }else{
            sb.append("MATERIAL / SUPPLY")
                .append("\nPURPOSE: inventory, crafting or scavenging")
                .append("\nACTIVE COMBAT BONUS: none");
        }
        sb.append("\nUNIT WEIGHT: ").append(game.itemMassLabelV141(type,1))
            .append("  •  STACK WEIGHT: ").append(game.itemMassLabelV141(type,quantity))
            .append("\nSTACK QUANTITY: ").append(quantity);
        return sb.toString();
    }
}

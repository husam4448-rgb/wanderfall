package com.survivalparadise.nativegame;

/** V97 non-hostile NPC dialogue scripts with distinct occupational responses.
 * Buttons are created in MainActivity; every non-exit action produces an effect.
 */
public final class NPCDialogueV97 {
    private NPCDialogueV97(){}
    public static final String[] ROLES={
        "TRADER","MEDIC","GUARD","MECHANIC","SURVIVOR"};
    public static final String[] QUESTIONS={
        "Ask about the settlement","Ask about nearby dangers",
        "Ask where to find supplies"};
    private static final String[][] ANSWERS={
        {"The settlement survives on scavenging and fair exchanges.",
         "Avoid hostile camps and stay inside lit corridors at night.",
         "Search storage cases in accessible buildings for materials."},
        {"Keep bandages and clean water ready before every expedition.",
         "Infected enemies and raiders can occupy abandoned rooms.",
         "Medical supplies are most common around clinics and first-aid cabinets."},
        {"Guards protect our people. Help the settlement to earn trust.",
         "Raiders patrol the outskirts; check corners before approaching.",
         "Secure facilities and supply depots may contain useful gear."},
        {"I repair tools and improvise with whatever scrap is available.",
         "Broken machines and damaged interiors can hide dangerous hazards.",
         "Search workshops, industrial buildings, and salvage piles."},
        {"I'm staying alive one day at a time. Allies make that easier.",
         "Zombies and hostile survivors can emerge from empty buildings.",
         "Check cabinets, backpacks and containers before leaving a room."}
    };
    public static String answer(int role,int question){
        return ANSWERS[Math.max(0,Math.min(4,role))]
            [Math.max(0,Math.min(2,question))];
    }
    public static boolean recruitable(int role){return role==2||role==4;}
}

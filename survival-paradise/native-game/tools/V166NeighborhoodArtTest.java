package com.survivalparadise.nativegame;

public final class V166NeighborhoodArtTest {
    private static void check(boolean ok,String message){
        if(!ok)throw new AssertionError(message);
    }
    public static void main(String[] args){
        check(BuildingArtSelectionV166.TYPES==NeighborhoodV154.TYPES,"kind drift");
        check(BuildingArtSelectionV166.SPRITES==16,"atlas drift");
        check(BuildingArtSelectionV166.choose(-1,0,1,0,0,0)==-1,"bad kind");
        check(BuildingArtSelectionV166.choose(8,0,1,0,0,0)==-1,"bad kind");
        for(int kind=0;kind<8;kind++){
            int variants=0;int changedSeed=0;
            for(int i=0;i<150;i++){
                int a=BuildingArtSelectionV166.choose(kind,i%12,14901,
                    i*17-800,i*31-300,i%6);
                int same=BuildingArtSelectionV166.choose(kind,i%12,14901,
                    i*17-800,i*31-300,i%6);
                int different=BuildingArtSelectionV166.choose(kind,i%12,84019,
                    i*17-800,i*31-300,i%6);
                check(a==same&&BuildingArtSelectionV166.valid(a),"not deterministic");
                check(a%8==kind,"wrong class art or atlas cell");
                check(BuildingArtSelectionV166.valid(different),"alternate seed invalid");
                if(a!=different)changedSeed++;
                variants|=1<<(a/8);
            }
            check(variants==3,"both variations must appear, kind "+kind);
            check(changedSeed>30,"seed must affect visual variants: "+kind);
        }
        check(BuildingArtSelectionV166.CELL==320,"atlas cell drift");
        System.out.println("PASS V166 neighborhoods: 8 classes × 2 authored sprites; seed stability + variation");
    }
}

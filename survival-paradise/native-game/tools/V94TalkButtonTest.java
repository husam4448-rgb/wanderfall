package com.survivalparadise.nativegame;

public final class V94TalkButtonTest {
    private static void ok(boolean valid,String why){
        if(!valid)throw new AssertionError(why);
    }
    public static void main(String[] args){
        ok(!ContextualTalkV94.visible(false,true,false,false,true,-1),
            "TALK cannot display without a nearby NPC");
        ok(ContextualTalkV94.visible(false,true,false,false,true,4),
            "friendly NPC activates contextual talk");
        ok(!ContextualTalkV94.visible(false,true,true,false,true,4),
            "pause hides button");
        ok(!ContextualTalkV94.visible(false,true,false,true,true,4),
            "game over hides button");
        ok(!ContextualTalkV94.visible(false,true,false,false,false,4),
            "disabled HUD control stays hidden");
        ok(ContextualTalkV94.visible(true,false,true,false,false,-1),
            "HUD editor shows an editable button at any location");
        ok(!ContextualTalkV94.canTalk(true,true,false,false,true,4),
            "editing cannot launch conversations");
        ok(!ContextualTalkV94.canTalk(false,true,false,false,true,-1),
            "no NPC cannot launch a conversation");
        ok(ContextualTalkV94.canTalk(false,true,false,false,true,1),
            "non-hostile medic opens talk");
        ok(ContextualTalkV94.inBounds(240f,100f,200f,80f,105f,44f),
            "dragged button hit region");
        ok(!ContextualTalkV94.inBounds(500f,500f,200f,80f,105f,44f),
            "unrelated tap must not trigger talk");
        System.out.println("V94 PASS: talk visibility, editor behavior, safe tap hit and no-NPC interaction");
    }
}
import React from "react";
import { Composition } from "remotion";
import { BridgeShort, BRIDGE_FRAMES } from "./videos/bridge/Bridge";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="BridgeShort"
        component={BridgeShort}
        fps={30}
        durationInFrames={BRIDGE_FRAMES}
        width={1080}
        height={1920}
      />
    </>
  );
};

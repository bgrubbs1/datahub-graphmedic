import React from 'react';
import {Composition} from 'remotion';
import {GraphMedicDemo} from './video';

export const Root: React.FC = () => (
  <Composition
    id="GraphMedicDemo"
    component={GraphMedicDemo}
    durationInFrames={3600}
    fps={30}
    width={1920}
    height={1080}
  />
);

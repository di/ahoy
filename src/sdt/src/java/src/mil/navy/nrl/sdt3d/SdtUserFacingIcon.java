package mil.navy.nrl.sdt3d;

import gov.nasa.worldwind.geom.Position;
import gov.nasa.worldwind.render.UserFacingIcon;
import gov.nasa.worldwind.WorldWindow;
public class SdtUserFacingIcon extends UserFacingIcon {

	SdtNode sdtNode;
	
	public SdtUserFacingIcon(SdtNode theNode,String iconPath, Position iconPosition)
	   {
	     super(iconPath,iconPosition);
	     sdtNode = theNode;
	   }

	public Position getPosition()
	   {
			// Get the latest globe elevation and update the nodes elevation
			Position pos =  super.getPosition();
			Position oldPos = sdtNode.getPosition();
			double globeElevation = sdt3d.AppFrame.getWwd().getModel().getGlobe().getElevation(pos.getLatitude(),pos.getLongitude());
			// If node is under msl, lock it to the surface.  Note that some land
			// areas are under msl so this hack will break that.
			if (sdtNode.getFollowTerrain())
			{	// If node is at terrain level, set node elev to globe elevation
				pos = new Position(pos.getLatitude(),pos.getLongitude(),globeElevation);
		    	sdtNode.resetPosition(pos);
		    	// ljt isn't this broken ? alt should always be zero ...
		    	if (oldPos.getElevation() != sdtNode.getAltitude() + globeElevation || globeElevation == 0)
		    	{
					sdtNode.updateLinks();
		    	}
				return pos;
			} else
			{
				if (!sdtNode.getUseAbsoluteElevation())
				{	// If node is at agl, set node elev to alt + globe elevation
					pos = new Position(pos.getLatitude(),pos.getLongitude(),sdtNode.getAltitude() + globeElevation);
					sdtNode.setPosition(pos);
					// If elevation has changed trigger link update
					// (or if we're over the ocean (globeElevation == 0)
					
					if (oldPos.getElevation() != sdtNode.getAltitude() + globeElevation || globeElevation == 0)
					{
						sdtNode.updateLinks();	
					}
					return pos;
				}
			}
			// Otherwise, just leave the node where it is
 			sdtNode.updateLinks();	    	
	        return super.getPosition();
	    }

}

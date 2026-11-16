<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" version="1.0.0" xmlns:gml="http://www.opengis.net/gml" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc">
  <UserLayer>
    <sld:LayerFeatureConstraints>
      <sld:FeatureTypeConstraint/>
    </sld:LayerFeatureConstraints>
    <sld:UserStyle>
      <sld:Name>Number of people per 250 square meters (2015)</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:ChannelSelection>
              <sld:GrayChannel>
                <sld:SourceChannelName>1</sld:SourceChannelName>
              </sld:GrayChannel>
            </sld:ChannelSelection>
       
            <sld:ColorMap type="ramp">
              <sld:ColorMapEntry quantity="0" label="0" color="#fff5f0"/>
              <sld:ColorMapEntry quantity="5" label="5" color="#fee0d2"/>
              <sld:ColorMapEntry quantity="10" label="10" color="#fcbba1"/>
              <sld:ColorMapEntry quantity="15" label="15" color="#fc9272"/>
              <sld:ColorMapEntry quantity="20" label="20" color="#fb6a4a"/>
              <sld:ColorMapEntry quantity="25" label="25" color="#ef3b2c"/>
              <sld:ColorMapEntry quantity="30" label="30" color="#cb181d"/>
              <sld:ColorMapEntry quantity="35" label="35" color="#a50f15"/>
              <sld:ColorMapEntry quantity="38" label="> 35" color="#67000d"/>
            </sld:ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </UserLayer>
</StyledLayerDescriptor>
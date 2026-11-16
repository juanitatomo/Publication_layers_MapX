<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" version="1.0.0" xmlns:sld="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc">
  <UserLayer>
    <sld:LayerFeatureConstraints>
      <sld:FeatureTypeConstraint/>
    </sld:LayerFeatureConstraints>
    <sld:UserStyle>
      <sld:Name>seismic_hazard_475</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:ChannelSelection>
              <sld:GrayChannel>
                <sld:SourceChannelName>1</sld:SourceChannelName>
              </sld:GrayChannel>
            </sld:ChannelSelection>
            <sld:ColorMap type="ramp">
              <sld:ColorMapEntry opacity="0" quantity="0" label="" color="#ffffff"/>
              <sld:ColorMapEntry quantity="0.1" label="0.1g" color="#036809"/>
              <sld:ColorMapEntry quantity="0.2" label="0.2g" color="#2db066"/>
              <sld:ColorMapEntry quantity="0.3" label="0.3g" color="#ffdf6d"/>
              <sld:ColorMapEntry quantity="0.4" label="0.4g" color="#f69053"/>
              <sld:ColorMapEntry quantity="0.5" label="0.5g" color="#a20002"/>
            </sld:ColorMap>
            <sld:VendorOption name="brightness">0.496078</sld:VendorOption>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </UserLayer>
</StyledLayerDescriptor>
<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:sld="http://www.opengis.net/sld" version="1.0.0" xmlns:gml="http://www.opengis.net/gml">
  <UserLayer>
    <sld:LayerFeatureConstraints>
      <sld:FeatureTypeConstraint/>
    </sld:LayerFeatureConstraints>
    <sld:UserStyle>
      <sld:Name>biomes_caucasus_clip</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:ChannelSelection>
              <sld:GrayChannel>
                <sld:SourceChannelName>1</sld:SourceChannelName>
              </sld:GrayChannel>
            </sld:ChannelSelection>
            <sld:ColorMap type="values">
              <sld:ColorMapEntry color="#2cea38" label="Temperate forest" quantity="3"/>
              <sld:ColorMapEntry color="#8bfa8b" label="Boreal forest" quantity="4"/>
              <sld:ColorMapEntry color="#f41400" label="Savanna and dry woodland" quantity="5"/>
              <sld:ColorMapEntry color="#fea11f" label="Grassland and dry shrubland" quantity="6"/>
              <sld:ColorMapEntry color="#fefa00" label="Desert" quantity="7"/>
              <sld:ColorMapEntry color="#27fff8" label="Tundra" quantity="8"/>
            </sld:ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </UserLayer>
</StyledLayerDescriptor>
